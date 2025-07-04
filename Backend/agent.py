"""
Main Compliance RAG Agent class
"""

import os
from typing import List, Dict, Any

# Core LangChain imports
from langchain_ibm import WatsonxEmbeddings, WatsonxLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools.render import render_text_description_and_args
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents import AgentExecutor
from langchain_core.runnables import RunnablePassthrough
from langchain.schema import Document

# IBM Watson AI imports
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import EmbeddingTypes

# Vector database imports
from langchain_astradb.vectorstores import AstraDBVectorStore

# Local imports
from config import Config
from parsers import CustomAgentOutputParser
from tools import create_compliance_tools
from utils import process_files_to_documents


class ComplianceRAGAgent:
    """
    A RAG-based compliance analysis system for legal document analysis.
    """
    
    def __init__(self, config: Config = None):
        """Initialize the compliance RAG agent with necessary configurations."""
        self.config = config or Config()
        self.setup_llm_and_embeddings()
        self.setup_vectorstores()
        self.setup_global_variables()
        self.initialize_tools()
        self.setup_agent()
        
    def setup_llm_and_embeddings(self):
        """Initialize Watson LLM and embedding models."""
        self.llm = WatsonxLLM(
            model_id="ibm/granite-3-2b-instruct",
            url=self.config.watsonx_credentials.get("url"),
            apikey=self.config.watsonx_credentials.get("apikey"),
            project_id=self.config.project_id,
            params={
                GenParams.DECODING_METHOD: "greedy",
                GenParams.TEMPERATURE: 0,
                GenParams.MIN_NEW_TOKENS: 5,
                GenParams.MAX_NEW_TOKENS: 500,
                GenParams.STOP_SEQUENCES: ["Human:", "Observation"],
            },
        )

        # Use a different embedding model that produces 768-dimensional vectors
        self.embeddings = WatsonxEmbeddings(
            model_id=EmbeddingTypes.IBM_SLATE_30M_ENG.value,
            url=self.config.watsonx_credentials["url"],
            apikey=self.config.watsonx_credentials["apikey"],
            project_id=self.config.project_id,
        )

    def setup_vectorstores(self):
        """Set up AstraDB vector stores for compliance documents."""
        try:
            # Company documents vectorstore (for compliance docs)
            self.company_vectorstore = AstraDBVectorStore(
                collection_name="company_compliance_docs",
                embedding=self.embeddings,
                api_endpoint=self.config.astra_db_api_endpoint,
                token=self.config.astra_db_application_token,
            )
        except Exception as e:
            print(f"Warning: Could not initialize company vectorstore: {e}")
            self.company_vectorstore = None

        try:
            # Pre-loaded regulations vectorstore (read-only)
            self.regulations_vectorstore = AstraDBVectorStore(
                collection_name="government_regulations",
                embedding=self.embeddings,
                api_endpoint=self.config.regulations_astra_endpoint,
                token=self.config.regulations_astra_token,
            )
        except Exception as e:
            print(f"Warning: Could not initialize regulations vectorstore: {e}")
            self.regulations_vectorstore = None

    def setup_global_variables(self):
        """Initialize global variables for compliance analysis state."""
        self.company_documents = []  # List to store processed document chunks
        self.company_context = {}    # Company metadata and description
        self.compliance_findings = {}  # Store analysis results per regulation
        self.uploaded_files_processed = False  # Flag to track if files are loaded

    def initialize_tools(self):
        """Initialize all tools for the agent."""
        self.tools = create_compliance_tools(self)

    def setup_agent(self):
        """Set up the agent with prompts and memory."""
        # Simplified system prompt for compliance analysis
        system_prompt = """You are a compliance expert assistant. You have access to these tools: {tools}

Your workflow:
1. Use ingest_company_documents to setup with company description
2. Use process_uploaded_files to confirm file processing
3. Use compliance_gap_analysis for regulation analysis (GDPR, NIST, HIPAA, etc.)
4. Use generate_compliance_report for final report

Always respond with valid JSON in this exact format:
{{
  "action": "tool_name",
  "action_input": "simple string input"
}}

Valid actions: {tool_names} or "Final Answer"

Examples:
{{
  "action": "ingest_company_documents",
  "action_input": "TechCorp - software company"
}}

{{
  "action": "compliance_gap_analysis", 
  "action_input": "GDPR"
}}

{{
  "action": "Final Answer",
  "action_input": "Your response here"
}}

IMPORTANT: 
- action_input must be a simple string, never a dictionary
- Always use valid JSON format
- No extra text before or after the JSON"""

        human_prompt = """{input}
{agent_scratchpad}"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", human_prompt),
        ])

        prompt = prompt.partial(
            tools=render_text_description_and_args(list(self.tools)),
            tool_names=", ".join([t.name for t in self.tools]),
        )

        # Create agent chain with better error handling
        chain = (
            RunnablePassthrough.assign(
                agent_scratchpad=lambda x: format_log_to_str(x["intermediate_steps"]),
                chat_history=lambda x: [],  # Empty chat history for now
            )
            | prompt
            | self.llm
            | CustomAgentOutputParser()
        )

        self.agent_executor = AgentExecutor(
            agent=chain, 
            tools=self.tools, 
            handle_parsing_errors=True, 
            verbose=False,  # Disabled verbose logging to prevent callback errors
            max_iterations=5,  # Reduced from 10 to prevent long loops
            return_intermediate_steps=True
        )

    def process_uploaded_files_sync(self, file_paths: List[str]) -> int:
        """Process uploaded files synchronously using local file paths
        
        Args:
            file_paths: List of file paths to process
            
        Returns:
            Number of document chunks processed
        """
        try:
            self.company_documents = process_files_to_documents(file_paths)
            
            self.company_context['document_chunks'] = len(self.company_documents)
            self.company_context['processed_files'] = [
                os.path.basename(f) for f in file_paths 
                if any(d.metadata.get('processed_file') == os.path.basename(f) for d in self.company_documents)
            ]
            self.uploaded_files_processed = True
            
            return len(self.company_documents)
            
        except Exception as e:
            print(f"Error in file processing: {str(e)}")
            return 0

    def reset_compliance_session(self):
        """Reset all compliance-related global variables for a new analysis"""
        self.company_documents = []
        self.company_context = {}
        self.compliance_findings = {}
        self.uploaded_files_processed = False
        
        print("✓ Compliance session reset. Ready for new analysis.")

    def show_compliance_status(self):
        """Display current status of compliance analysis"""
        print("=== COMPLIANCE ANALYSIS STATUS ===")
        print(f"Company Description: {self.company_context.get('description', 'Not set')}")
        print(f"Files Processed: {self.uploaded_files_processed}")
        print(f"Document Chunks: {len(self.company_documents)}")
        print(f"Regulations Analyzed: {list(self.compliance_findings.keys())}")
        print(f"Ready for Report: {'Yes' if self.compliance_findings else 'No'}")

    def invoke(self, input_text: str):
        """Invoke the agent with input text."""
        return self.agent_executor.invoke({"input": input_text})

    def invoke_direct(self, tool_name: str, tool_input: str):
        """Invoke a tool directly without using the agent executor."""
        try:
            # Find the tool by name
            tool = None
            for t in self.tools:
                if t.name == tool_name:
                    tool = t
                    break
            
            if tool is None:
                return {"error": f"Tool '{tool_name}' not found"}
            
            # Invoke the tool directly
            result = tool.invoke(tool_input)
            return {"output": result}
            
        except Exception as e:
            return {"error": str(e)}
