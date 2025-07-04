"""
Compliance RAG Agent for Legal Document Analysis
===============================================

This module provides a RAG-based compliance analysis system that can:
1. Analyze company documents against various regulations (GDPR, NIST, HIPAA, etc.)
2. Generate compliance gap analysis reports
3. Process uploaded company documents for compliance assessment

Author: Your Name
Date: 2025
"""

import os
import tempfile
from typing import List, Dict, Any
from pathlib import Path

# Set USER_AGENT to avoid warning
os.environ["USER_AGENT"] = "compliance-rag-agent/1.0"

# Core LangChain imports
from langchain_ibm import WatsonxEmbeddings, WatsonxLLM
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain.tools.render import render_text_description_and_args
from langchain.agents.output_parsers import JSONAgentOutputParser
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents import AgentExecutor
from langchain_core.runnables import RunnablePassthrough
from langchain.schema import Document
from langchain_core.output_parsers import BaseOutputParser
import json
import re

# IBM Watson AI imports
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.utils.enums import EmbeddingTypes

# Vector database imports
from astrapy import DataAPIClient
from langchain_astradb.vectorstores import AstraDBVectorStore

# Utility imports
from ibm_granite_community.notebook_utils import get_env_var

# Flask imports for web interface
from flask import Flask, request, render_template_string, jsonify, send_from_directory
import werkzeug

class CustomAgentOutputParser(BaseOutputParser):
    """Custom output parser that can handle various LLM output formats."""
    
    def parse(self, text: str):
        """Parse the LLM output to extract action and action_input."""
        try:
            # Try to find JSON in the text
            json_match = re.search(r'\{[^{}]*"action"[^{}]*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                return parsed
            
            # If no JSON found, try to extract action from text
            if "Final Answer" in text:
                # Extract the final answer
                final_answer_match = re.search(r'Final Answer[:\s]*(.+)', text, re.DOTALL)
                if final_answer_match:
                    answer = final_answer_match.group(1).strip()
                    return {
                        "action": "Final Answer",
                        "action_input": answer
                    }
            
            # Fallback: return a default response
            return {
                "action": "Final Answer",
                "action_input": "I understand your request. Please proceed with the next step."
            }
            
        except Exception as e:
            # If all parsing fails, return a default response
            return {
                "action": "Final Answer",
                "action_input": f"Parsing error occurred: {str(e)}. Please try again."
            }

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'compliance-rag-secret-key'

# Create uploads directory if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variables for the web interface
global_agent = None
uploaded_file_paths = []

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compliance RAG Agent</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .upload-section {
            border: 2px dashed #3498db;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            margin: 20px 0;
            background-color: #f8f9fa;
        }
        .upload-section:hover {
            border-color: #2980b9;
            background-color: #e3f2fd;
        }
        .file-input {
            display: none;
        }
        .upload-btn {
            background-color: #3498db;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
        }
        .upload-btn:hover {
            background-color: #2980b9;
        }
        .file-list {
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }
        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            margin: 5px 0;
            background: white;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        .remove-btn {
            background-color: #e74c3c;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 3px;
            cursor: pointer;
        }
        .remove-btn:hover {
            background-color: #c0392b;
        }
        .status {
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            font-weight: bold;
        }
        .status.success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status.error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .status.info {
            background-color: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .form-group {
            margin: 15px 0;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #2c3e50;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        textarea {
            height: 100px;
            resize: vertical;
        }
        .action-buttons {
            text-align: center;
            margin: 20px 0;
        }
        .action-btn {
            background-color: #27ae60;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
        }
        .action-btn:hover {
            background-color: #229954;
        }
        .action-btn:disabled {
            background-color: #95a5a6;
            cursor: not-allowed;
        }
        .results {
            margin-top: 20px;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 5px;
            white-space: pre-wrap;
            font-family: monospace;
            max-height: 400px;
            overflow-y: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Compliance RAG Agent</h1>
        
        <div class="form-group">
            <label for="company-description">Company Description:</label>
            <textarea id="company-description" placeholder="Describe your company and its business activities..."></textarea>
        </div>

        <div class="upload-section">
            <h3>📁 Upload Compliance Documents</h3>
            <p>Supported formats: PDF, DOCX, TXT, MD</p>
            <input type="file" id="file-input" class="file-input" multiple accept=".pdf,.docx,.txt,.md">
            <button class="upload-btn" onclick="document.getElementById('file-input').click()">Choose Files</button>
            <button class="upload-btn" onclick="uploadFiles()">Upload Files</button>
        </div>

        <div id="file-list" class="file-list" style="display: none;">
            <h4>Selected Files:</h4>
            <div id="file-items"></div>
        </div>

        <div id="status"></div>

        <div class="action-buttons">
            <button class="action-btn" onclick="setupIngestion()">Setup Document Ingestion</button>
            <button class="action-btn" onclick="processFiles()" id="process-btn" disabled>Process Uploaded Files</button>
            <button class="action-btn" onclick="analyzeGDPR()" id="analyze-btn" disabled>Analyze GDPR Compliance</button>
            <button class="action-btn" onclick="generateReport()" id="report-btn" disabled>Generate Report</button>
        </div>

        <div id="results" class="results" style="display: none;"></div>
    </div>

    <script>
        let uploadedFiles = [];
        let companyDescription = '';

        document.getElementById('file-input').addEventListener('change', function(e) {
            const files = Array.from(e.target.files);
            uploadedFiles = files;
            displayFiles(files);
        });

        function displayFiles(files) {
            const fileList = document.getElementById('file-list');
            const fileItems = document.getElementById('file-items');
            
            if (files.length === 0) {
                fileList.style.display = 'none';
                return;
            }

            fileList.style.display = 'block';
            fileItems.innerHTML = '';

            files.forEach((file, index) => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                fileItem.innerHTML = `
                    <span>${file.name} (${(file.size / 1024).toFixed(1)} KB)</span>
                    <button class="remove-btn" onclick="removeFile(${index})">Remove</button>
                `;
                fileItems.appendChild(fileItem);
            });
        }

        function removeFile(index) {
            uploadedFiles.splice(index, 1);
            displayFiles(uploadedFiles);
        }

        function showStatus(message, type = 'info') {
            const status = document.getElementById('status');
            status.innerHTML = `<div class="status ${type}">${message}</div>`;
        }

        function showResults(data) {
            const results = document.getElementById('results');
            results.style.display = 'block';
            results.textContent = data;
        }

        async function uploadFiles() {
            if (uploadedFiles.length === 0) {
                showStatus('Please select files first', 'error');
                return;
            }

            const formData = new FormData();
            uploadedFiles.forEach(file => {
                formData.append('files', file);
            });

            try {
                showStatus('Uploading files...', 'info');
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                if (result.success) {
                    showStatus(`Successfully uploaded ${result.files.length} files`, 'success');
                    document.getElementById('process-btn').disabled = false;
                } else {
                    showStatus('Upload failed: ' + result.error, 'error');
                }
            } catch (error) {
                showStatus('Upload error: ' + error.message, 'error');
            }
        }

        async function setupIngestion() {
            companyDescription = document.getElementById('company-description').value.trim();
            if (!companyDescription) {
                showStatus('Please enter a company description', 'error');
                return;
            }

            try {
                showStatus('Setting up document ingestion...', 'info');
                const response = await fetch('/setup_ingestion', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({company_description: companyDescription})
                });
                
                const result = await response.json();
                if (result.success) {
                    showStatus('Document ingestion setup complete', 'success');
                    showResults(result.message);
                } else {
                    showStatus('Setup failed: ' + result.error, 'error');
                }
            } catch (error) {
                showStatus('Setup error: ' + error.message, 'error');
            }
        }

        async function processFiles() {
            try {
                showStatus('Processing uploaded files...', 'info');
                const response = await fetch('/process_files', {
                    method: 'POST'
                });
                
                const result = await response.json();
                if (result.success) {
                    showStatus(`Processed ${result.chunks} document chunks`, 'success');
                    document.getElementById('analyze-btn').disabled = false;
                    showResults(result.message);
                } else {
                    showStatus('Processing failed: ' + result.error, 'error');
                }
            } catch (error) {
                showStatus('Processing error: ' + error.message, 'error');
            }
        }

        async function analyzeGDPR() {
            try {
                showStatus('Analyzing GDPR compliance...', 'info');
                const response = await fetch('/analyze_gdpr', {
                    method: 'POST'
                });
                
                const result = await response.json();
                if (result.success) {
                    showStatus('GDPR analysis complete', 'success');
                    document.getElementById('report-btn').disabled = false;
                    showResults(result.message);
                } else {
                    showStatus('Analysis failed: ' + result.error, 'error');
                }
            } catch (error) {
                showStatus('Analysis error: ' + error.message, 'error');
            }
        }

        async function generateReport() {
            try {
                showStatus('Generating compliance report...', 'info');
                const response = await fetch('/generate_report', {
                    method: 'POST'
                });
                
                const result = await response.json();
                if (result.success) {
                    showStatus('Report generated successfully', 'success');
                    showResults(result.report);
                } else {
                    showStatus('Report generation failed: ' + result.error, 'error');
                }
            } catch (error) {
                showStatus('Report error: ' + error.message, 'error');
            }
        }
    </script>
</body>
</html>
"""

class ComplianceRAGAgent:
    """
    A RAG-based compliance analysis system for legal document analysis.
    """
    
    def __init__(self):
        """Initialize the compliance RAG agent with necessary configurations."""
        self.setup_credentials()
        self.initialize_llm_and_embeddings()
        self.setup_vectorstores()
        self.setup_global_variables()
        self.initialize_tools()
        self.setup_agent()
        
    def setup_credentials(self):
        """Set up Watson AI and AstraDB credentials from environment variables."""
        self.credentials = {
            "url": get_env_var("WATSONX_URL"),
            "apikey": get_env_var("WATSONX_APIKEY")
        }
        self.project_id = get_env_var("WATSONX_PROJECT_ID")
        
        # AstraDB credentials for company docs
        self.astra_db_api_endpoint = get_env_var("ASTRA_DB_API_ENDPOINT")
        self.astra_db_application_token = get_env_var("ASTRA_DB_APPLICATION_TOKEN")
        
        # Pre-loaded regulations database (separate AstraDB instance)
        self.regulations_astra_endpoint = get_env_var("REGULATIONS_ASTRA_ENDPOINT")
        self.regulations_astra_token = get_env_var("REGULATIONS_ASTRA_TOKEN")

    def initialize_llm_and_embeddings(self):
        """Initialize Watson LLM and embedding models."""
        self.llm = WatsonxLLM(
            model_id="ibm/ibm/granite-3-2b-instruct",
            url=self.credentials.get("url"),
            apikey=self.credentials.get("apikey"),
            project_id=self.project_id,
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
            url=self.credentials["url"],
            apikey=self.credentials["apikey"],
            project_id=self.project_id,
        )

    def setup_vectorstores(self):
        """Set up AstraDB vector stores for compliance documents."""
        try:
            # Company documents vectorstore (for compliance docs)
            self.company_vectorstore = AstraDBVectorStore(
                collection_name="company_compliance_docs",
                embedding=self.embeddings,
                api_endpoint=self.astra_db_api_endpoint,
                token=self.astra_db_application_token,
            )
        except Exception as e:
            print(f"Warning: Could not initialize company vectorstore: {e}")
            self.company_vectorstore = None

        try:
            # Pre-loaded regulations vectorstore (read-only)
            self.regulations_vectorstore = AstraDBVectorStore(
                collection_name="government_regulations",
                embedding=self.embeddings,
                api_endpoint=self.regulations_astra_endpoint,
                token=self.regulations_astra_token,
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
        
        @tool  
        def ingest_company_documents(company_description: str, file_count: int = 0) -> str:
            """Load uploaded company compliance documents from browser uploads into memory for analysis.
            
            Args:
                company_description: Description of the company and its business
                file_count: Number of files uploaded (optional, for verification)
            """
            try:
                # Store company description
                self.company_context['description'] = company_description
                self.company_documents = []  # Clear previous documents
                
                self.company_context['files_ready'] = True
                self.uploaded_files_processed = False  # Will be set to True after manual processing
                
                return f"""
Document ingestion system ready for company: {company_description}

To complete the process:
1. Upload your compliance documents (PDF, DOCX, TXT, MD) using the file upload interface
2. Run the 'process_uploaded_compliance_files()' function in the next cell
3. Files will be processed in-memory (not stored in AstraDB)
4. Then proceed with compliance analysis

Supported formats: PDF, DOCX, TXT, MD
Processing mode: In-memory only (session-based)
Ready for file upload and processing.
"""
                
            except Exception as e:
                return f"Error in document ingestion setup: {str(e)}"

        @tool
        def process_uploaded_files() -> str:
            """Process files that have been uploaded to the notebook session."""
            if not self.uploaded_files_processed:
                return "Files not yet processed. Please run the 'process_uploaded_compliance_files()' function first after uploading your files."
            
            if not self.company_documents:
                return "No documents processed yet. Please upload and process files first."
            
            total_chunks = len(self.company_documents)
            self.company_context['document_chunks'] = total_chunks
            
            return f"Successfully processed {total_chunks} document chunks from uploaded files. Ready for compliance analysis."

        @tool
        def compliance_gap_analysis(regulation_type: str) -> str:
            """Analyze company documents against specific regulation using pre-loaded regulations DB.
            
            Args:
                regulation_type: Type of regulation (GDPR, NIST, HIPAA, ISO27001, etc.)
            """
            if not self.company_documents:
                return "No company documents loaded. Please upload and process files first using ingest_company_documents and process_uploaded_files."
            
            try:
                # Get regulation requirements (simplified approach without vectorstore)
                regulation_requirements = self.get_regulation_requirements(regulation_type)
                
                # Use in-memory company documents for analysis
                relevant_company_docs = self.company_documents[:15]  # Take first 15 chunks
                
                # Combine contexts for LLM analysis
                reg_context = regulation_requirements
                company_doc_context = "\n".join([doc.page_content for doc in relevant_company_docs])
                
                # LLM prompt for gap analysis
                analysis_prompt = f"""
You are a compliance expert. Analyze the company's documentation against {regulation_type} requirements.

REGULATION REQUIREMENTS:
{reg_context}

COMPANY DOCUMENTATION:
{company_doc_context}

COMPANY DESCRIPTION: {self.company_context.get('description', 'Not provided')}

Provide a structured analysis with:
1. COMPLIANT: Areas where company meets requirements
2. GAPS: Missing or non-compliant areas  
3. PARTIAL: Areas with partial implementation
4. RISK_LEVEL: High/Medium/Low for each gap

Format each finding as: SECTION|STATUS|DESCRIPTION|RISK_LEVEL

Provide specific, actionable findings based on the documentation provided.
"""
                
                analysis_result = self.llm.invoke(analysis_prompt)
                self.compliance_findings[regulation_type] = analysis_result
                
                return f"Completed {regulation_type} gap analysis using {len(relevant_company_docs)} company document chunks. Results stored for report generation."
                
            except Exception as e:
                return f"Error in compliance gap analysis: {str(e)}"

        @tool(return_direct=True)
        def generate_compliance_report() -> str:
            """Generate comprehensive compliance assessment report from all analyses."""
            if not self.compliance_findings:
                return "No compliance analysis data available. Please run gap analysis for at least one regulation first."
            
            try:
                # Compile report
                findings_summary = ""
                for regulation, analysis in self.compliance_findings.items():
                    findings_summary += f"\n\n=== {regulation} ANALYSIS ===\n{analysis}"
                
                report_prompt = f"""
Generate a professional compliance assessment report based on the following analysis:

COMPANY: {self.company_context.get('description', 'Company under assessment')}
DOCUMENT CHUNKS ANALYZED: {self.company_context.get('document_chunks', 'Not specified')}

ANALYSIS RESULTS:
{findings_summary}

Structure the report as:
# EXECUTIVE SUMMARY
Brief overview of overall compliance posture and key findings

# COMPANY OVERVIEW  
Brief description of the company and scope of assessment

# OVERALL COMPLIANCE POSTURE
High-level assessment across all regulations analyzed

# DETAILED FINDINGS BY REGULATION
For each regulation analyzed, provide:
- Compliant areas
- Identified gaps
- Partial implementations
- Risk assessments

# RISK PRIORITIZATION MATRIX
Categorize findings by risk level (High/Medium/Low) and impact

# REMEDIATION RECOMMENDATIONS
Actionable recommendations for addressing gaps, organized by priority

# IMPLEMENTATION TIMELINE
Suggested timeline for addressing findings

# CONCLUSION
Summary and next steps

Make it professional, actionable, and specific to the findings provided.
"""
                
                final_report = self.llm.invoke(report_prompt)
                
                # Add metadata to report
                metadata_header = f"""
COMPLIANCE ASSESSMENT REPORT
Generated: {self.company_context.get('description', 'Unknown Company')}
Regulations Analyzed: {', '.join(self.compliance_findings.keys())}
Document Chunks: {self.company_context.get('document_chunks', 'Not specified')}
Analysis Date: Auto-generated

{'='*60}
"""
                
                return metadata_header + final_report
                
            except Exception as e:
                return f"Error generating compliance report: {str(e)}"

        # Store tools for agent
        self.tools = [ingest_company_documents, process_uploaded_files, compliance_gap_analysis, generate_compliance_report]

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

    async def process_uploaded_compliance_files(self, uploaded_filenames: List[str]):
        """Process uploaded files using window.fs.readFile API
        
        Args:
            uploaded_filenames: List of filenames to process
        """
        try:
            # Initialize text splitter
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=300, chunk_overlap=50
            )
            
            self.company_documents = []
            
            print("Starting file processing...")
            
            for filename in uploaded_filenames:
                try:
                    print(f"Processing {filename}...")
                    
                    if filename.endswith('.pdf'):
                        # Read PDF file
                        file_content = await window.fs.readFile(filename)
                        
                        # Create temporary file for PDF processing
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                            tmp_file.write(file_content)
                            
                            # Process with PyPDFLoader
                            loader = PyPDFLoader(tmp_file.name)
                            documents = loader.load()
                            
                            # Clean up temp file
                            os.unlink(tmp_file.name)
                    
                    elif filename.endswith('.txt') or filename.endswith('.md'):
                        # Read text file
                        file_content = await window.fs.readFile(filename, {'encoding': 'utf8'})
                        documents = [Document(
                            page_content=file_content, 
                            metadata={'source': filename, 'type': 'text'}
                        )]
                    
                    elif filename.endswith('.docx'):
                        # Read DOCX file
                        file_content = await window.fs.readFile(filename)
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                            tmp_file.write(file_content)
                            
                            loader = Docx2txtLoader(tmp_file.name)
                            documents = loader.load()
                            
                            os.unlink(tmp_file.name)
                    
                    else:
                        print(f"Unsupported file type: {filename}")
                        continue
                    
                    # Split documents into chunks
                    doc_splits = text_splitter.split_documents(documents)
                    
                    # Add metadata
                    for doc in doc_splits:
                        doc.metadata['processed_file'] = filename
                        doc.metadata['chunk_size'] = len(doc.page_content)
                    
                    self.company_documents.extend(doc_splits)
                    
                    print(f"✓ Processed {filename}: {len(doc_splits)} chunks")
                    
                except Exception as e:
                    print(f"✗ Error processing {filename}: {str(e)}")
                    continue
            
            print(f"\n📄 Total processed: {len(self.company_documents)} document chunks")
            self.company_context['document_chunks'] = len(self.company_documents)
            self.company_context['processed_files'] = [f for f in uploaded_filenames if any(d.metadata.get('processed_file') == f for d in self.company_documents)]
            self.uploaded_files_processed = True
            
            return len(self.company_documents)
            
        except Exception as e:
            print(f"Error in file processing: {str(e)}")
            return 0

    def process_uploaded_files_sync(self, file_paths: List[str]):
        """Process uploaded files synchronously using local file paths
        
        Args:
            file_paths: List of file paths to process
        """
        try:
            # Initialize text splitter
            text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                chunk_size=300, chunk_overlap=50
            )
            
            self.company_documents = []
            
            print("Starting file processing...")
            
            for file_path in file_paths:
                try:
                    filename = os.path.basename(file_path)
                    print(f"Processing {filename}...")
                    
                    if filename.endswith('.pdf'):
                        # Process PDF file directly
                        loader = PyPDFLoader(file_path)
                        documents = loader.load()
                    
                    elif filename.endswith('.txt') or filename.endswith('.md'):
                        # Read text file
                        with open(file_path, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                        documents = [Document(
                            page_content=file_content, 
                            metadata={'source': filename, 'type': 'text'}
                        )]
                    
                    elif filename.endswith('.docx'):
                        # Process DOCX file directly
                        loader = Docx2txtLoader(file_path)
                        documents = loader.load()
                    
                    else:
                        print(f"Unsupported file type: {filename}")
                        continue
                    
                    # Split documents into chunks
                    doc_splits = text_splitter.split_documents(documents)
                    
                    # Add metadata
                    for doc in doc_splits:
                        doc.metadata['processed_file'] = filename
                        doc.metadata['chunk_size'] = len(doc.page_content)
                    
                    self.company_documents.extend(doc_splits)
                    
                    print(f"✓ Processed {filename}: {len(doc_splits)} chunks")
                    
                except Exception as e:
                    print(f"✗ Error processing {filename}: {str(e)}")
                    continue
            
            print(f"\n📄 Total processed: {len(self.company_documents)} document chunks")
            self.company_context['document_chunks'] = len(self.company_documents)
            self.company_context['processed_files'] = [os.path.basename(f) for f in file_paths if any(d.metadata.get('processed_file') == os.path.basename(f) for d in self.company_documents)]
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

    def get_regulation_requirements(self, regulation_type: str) -> str:
        """Get regulation requirements for the specified regulation type."""
        regulation_content = {
            "GDPR": """
General Data Protection Regulation (GDPR) Requirements:

1. DATA PROTECTION PRINCIPLES:
- Lawfulness, fairness, and transparency
- Purpose limitation
- Data minimization
- Accuracy
- Storage limitation
- Integrity and confidentiality
- Accountability

2. INDIVIDUAL RIGHTS:
- Right to be informed
- Right of access
- Right to rectification
- Right to erasure
- Right to restrict processing
- Right to data portability
- Right to object
- Rights in relation to automated decision making

3. ORGANIZATIONAL REQUIREMENTS:
- Data protection by design and by default
- Data protection impact assessments
- Data protection officer appointment
- Record of processing activities
- Security measures
- Breach notification procedures
- Cross-border data transfer safeguards

4. ACCOUNTABILITY MEASURES:
- Documentation and record keeping
- Staff training and awareness
- Regular audits and assessments
- Incident response procedures
- Vendor management and contracts
""",
            "NIST": """
NIST Cybersecurity Framework Requirements:

1. IDENTIFY:
- Asset management
- Business environment
- Governance
- Risk assessment
- Risk management strategy
- Supply chain risk management

2. PROTECT:
- Identity management and access control
- Awareness and training
- Data security
- Information protection processes and procedures
- Maintenance
- Protective technology

3. DETECT:
- Anomalies and events
- Security continuous monitoring
- Detection processes

4. RESPOND:
- Response planning
- Communications
- Analysis
- Mitigation
- Improvements

5. RECOVER:
- Recovery planning
- Improvements
- Communications
""",
            "HIPAA": """
Health Insurance Portability and Accountability Act (HIPAA) Requirements:

1. PRIVACY RULE:
- Notice of privacy practices
- Individual rights
- Uses and disclosures
- Administrative requirements
- Training and awareness

2. SECURITY RULE:
- Administrative safeguards
- Physical safeguards
- Technical safeguards
- Organizational requirements
- Policies and procedures

3. BREACH NOTIFICATION RULE:
- Breach assessment
- Notification procedures
- Documentation requirements

4. ENFORCEMENT RULE:
- Compliance monitoring
- Penalties and sanctions
- Resolution procedures
""",
            "ISO27001": """
ISO/IEC 27001 Information Security Management System Requirements:

1. CONTEXT OF THE ORGANIZATION:
- Understanding the organization and its context
- Understanding the needs and expectations of interested parties
- Determining the scope of the ISMS
- Information security management system

2. LEADERSHIP:
- Leadership and commitment
- Policy
- Organizational roles, responsibilities, and authorities

3. PLANNING:
- Actions to address risks and opportunities
- Information security objectives and planning to achieve them

4. SUPPORT:
- Resources
- Competence
- Awareness
- Communication
- Documented information

5. OPERATION:
- Operational planning and control
- Information security risk assessment
- Information security risk treatment

6. PERFORMANCE EVALUATION:
- Monitoring, measurement, analysis, and evaluation
- Internal audit
- Management review

7. IMPROVEMENT:
- Nonconformity and corrective action
- Continual improvement
"""
        }
        
        return regulation_content.get(regulation_type.upper(), f"Basic requirements for {regulation_type} compliance analysis.")


def main():
    """Main function to run the Flask web application."""
    print("""
=== COMPLIANCE RAG AGENT WEB INTERFACE ===

Starting web server for compliance document analysis...

The web interface will be available at: http://localhost:5000

FEATURES:
- Upload compliance documents (PDF, DOCX, TXT, MD)
- Analyze against various regulations (GDPR, NIST, HIPAA, etc.)
- Generate comprehensive compliance reports
- Modern web interface with real-time status updates

WORKFLOW:
1. Open http://localhost:5000 in your browser
2. Enter company description
3. Upload compliance documents
4. Process files and run analysis
5. Generate compliance report

Press Ctrl+C to stop the server.
""")

    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)


@app.route('/')
def index():
    """Main page with file upload interface."""
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads."""
    global uploaded_file_paths
    
    try:
        if 'files' not in request.files:
            return jsonify({'success': False, 'error': 'No files provided'})
        
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file.filename == '':
                continue
                
            if file and allowed_file(file.filename):
                # Secure the filename
                filename = werkzeug.utils.secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                # Save the file
                file.save(filepath)
                uploaded_files.append(filename)
                uploaded_file_paths.append(filepath)
        
        return jsonify({
            'success': True, 
            'files': uploaded_files,
            'message': f'Successfully uploaded {len(uploaded_files)} files'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/setup_ingestion', methods=['POST'])
def setup_ingestion():
    """Setup document ingestion with company description."""
    global global_agent
    
    try:
        data = request.get_json()
        company_description = data.get('company_description', '')
        
        if not company_description:
            return jsonify({'success': False, 'error': 'Company description is required'})
        
        # Initialize the agent if not already done
        if global_agent is None:
            global_agent = ComplianceRAGAgent()
        
        # Try agent invocation first, fallback to direct tool call
        try:
            result = global_agent.invoke(f"Set up document ingestion for {company_description}")
            output = result.get('output', 'Document ingestion setup complete')
            if isinstance(output, dict):
                output = output.get('action_input', 'Document ingestion setup complete')
        except Exception as agent_error:
            # Fallback to direct tool invocation
            result = global_agent.invoke_direct("ingest_company_documents", company_description)
            output = result.get('output', 'Document ingestion setup complete')
        
        return jsonify({
            'success': True,
            'message': output
        })
        
    except Exception as e:
        error_message = handle_agent_error(e, 'setup ingestion')
        return jsonify({'success': False, 'error': error_message})

@app.route('/process_files', methods=['POST'])
def process_files():
    """Process uploaded files."""
    global global_agent, uploaded_file_paths
    
    try:
        if global_agent is None:
            return jsonify({'success': False, 'error': 'Agent not initialized. Please setup ingestion first.'})
        
        if not uploaded_file_paths:
            return jsonify({'success': False, 'error': 'No files uploaded. Please upload files first.'})
        
        # Process files using the agent's method
        chunks_processed = global_agent.process_uploaded_files_sync(uploaded_file_paths)
        
        return jsonify({
            'success': True,
            'chunks': chunks_processed,
            'message': f'Successfully processed {chunks_processed} document chunks'
        })
        
    except Exception as e:
        error_message = handle_agent_error(e, 'file processing')
        return jsonify({'success': False, 'error': error_message})

@app.route('/analyze_gdpr', methods=['POST'])
def analyze_gdpr():
    """Analyze GDPR compliance."""
    global global_agent
    
    try:
        if global_agent is None:
            return jsonify({'success': False, 'error': 'Agent not initialized.'})
        
        # Try agent invocation first, fallback to direct tool call
        try:
            result = global_agent.invoke("Analyze against GDPR")
            output = result.get('output', 'GDPR analysis completed')
            if isinstance(output, dict):
                output = output.get('action_input', 'GDPR analysis completed')
        except Exception as agent_error:
            # Fallback to direct tool invocation
            result = global_agent.invoke_direct("compliance_gap_analysis", "GDPR")
            output = result.get('output', 'GDPR analysis completed')
        
        return jsonify({
            'success': True,
            'message': output
        })
        
    except Exception as e:
        error_message = handle_agent_error(e, 'GDPR analysis')
        return jsonify({'success': False, 'error': error_message})

@app.route('/generate_report', methods=['POST'])
def generate_report():
    """Generate compliance report."""
    global global_agent
    
    try:
        if global_agent is None:
            return jsonify({'success': False, 'error': 'Agent not initialized.'})
        
        # Try agent invocation first, fallback to direct tool call
        try:
            result = global_agent.invoke("Generate comprehensive compliance report")
            output = result.get('output', 'Report generation completed')
            if isinstance(output, dict):
                output = output.get('action_input', 'Report generation completed')
        except Exception as agent_error:
            # Fallback to direct tool invocation
            result = global_agent.invoke_direct("generate_compliance_report", "")
            output = result.get('output', 'Report generation completed')
        
        return jsonify({
            'success': True,
            'report': output
        })
        
    except Exception as e:
        error_message = handle_agent_error(e, 'report generation')
        return jsonify({'success': False, 'error': error_message})

@app.route('/test_agent', methods=['GET'])
def test_agent():
    """Test if the agent is working properly."""
    global global_agent
    
    try:
        if global_agent is None:
            return jsonify({'success': False, 'error': 'Agent not initialized'})
        
        # Test with a simple direct tool call
        test_result = global_agent.tools[0].invoke("Test company - A technology company")
        
        return jsonify({
            'success': True,
            'message': 'Agent is working properly',
            'test_result': str(test_result)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/test_parser', methods=['GET'])
def test_parser():
    """Test the custom output parser."""
    try:
        parser = CustomAgentOutputParser()
        
        # Test cases
        test_cases = [
            '{"action": "ingest_company_documents", "action_input": "Test company"}',
            'Action:\n{"action": "Final Answer", "action_input": "Test response"}',
            'Final Answer: This is a test response',
            'Invalid JSON format'
        ]
        
        results = []
        for test_input in test_cases:
            try:
                result = parser.parse(test_input)
                results.append({
                    'input': test_input,
                    'output': result,
                    'success': True
                })
            except Exception as e:
                results.append({
                    'input': test_input,
                    'error': str(e),
                    'success': False
                })
        
        return jsonify({
            'success': True,
            'parser_test_results': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/test_compliance', methods=['GET'])
def test_compliance():
    """Test compliance analysis without vectorstores."""
    global global_agent
    
    try:
        if global_agent is None:
            return jsonify({'success': False, 'error': 'Agent not initialized'})
        
        # Test regulation requirements
        gdpr_req = global_agent.get_regulation_requirements("GDPR")
        
        return jsonify({
            'success': True,
            'message': 'Compliance analysis system is working',
            'gdpr_requirements_length': len(gdpr_req),
            'vectorstore_status': {
                'company_vectorstore': global_agent.company_vectorstore is not None,
                'regulations_vectorstore': global_agent.regulations_vectorstore is not None
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def allowed_file(filename):
    """Check if file extension is allowed."""
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'md'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def handle_agent_error(error, operation):
    """Handle agent errors gracefully."""
    error_msg = str(error)
    if "OUTPUT_PARSING_FAILURE" in error_msg:
        return f"Agent parsing error during {operation}. Please try again."
    elif "max_iterations" in error_msg:
        return f"Agent reached maximum iterations during {operation}. Please try a simpler request."
    else:
        return f"Error during {operation}: {error_msg}"

if __name__ == "__main__":
    main()