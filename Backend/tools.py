"""
Tools for the Compliance RAG Agent
"""

import json
import re
from typing import List, Dict, Any
from langchain.tools import tool
from utils import get_regulation_requirements


def create_compliance_tools(agent_instance):
    """Create compliance analysis tools for the agent."""
    
    @tool  
    def ingest_company_documents(company_description: str, file_count: int = 0) -> str:
        """Load uploaded company compliance documents from browser uploads into memory for analysis.
        
        Args:
            company_description: Description of the company and its business
            file_count: Number of files uploaded (optional, for verification)
        """
        try:
            # Store company description
            agent_instance.company_context['description'] = company_description
            agent_instance.company_documents = []  # Clear previous documents
            
            agent_instance.company_context['files_ready'] = True
            agent_instance.uploaded_files_processed = False  # Will be set to True after manual processing
            
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
        if not agent_instance.uploaded_files_processed:
            return "Files not yet processed. Please run the 'process_uploaded_compliance_files()' function first after uploading your files."
        
        if not agent_instance.company_documents:
            return "No documents processed yet. Please upload and process files first."
        
        total_chunks = len(agent_instance.company_documents)
        agent_instance.company_context['document_chunks'] = total_chunks
        
        return f"Successfully processed {total_chunks} document chunks from uploaded files. Ready for compliance analysis."

    @tool
    def compliance_gap_analysis(regulation_type: str) -> str:
        """Analyze company documents against specific regulation using pre-loaded regulations DB.
        
        Args:
            regulation_type: Type of regulation (GDPR, NIST, HIPAA, ISO27001, etc.)
        """
        if not agent_instance.company_documents:
            return "No company documents loaded. Please upload and process files first using ingest_company_documents and process_uploaded_files."
        
        try:
            # Get regulation requirements (simplified approach without vectorstore)
            regulation_requirements = get_regulation_requirements(regulation_type)
            
            # Use in-memory company documents for analysis
            relevant_company_docs = agent_instance.company_documents[:50]  # Take first 15 chunks
            
            # Combine contexts for LLM analysis
            reg_context = regulation_requirements
            company_doc_context = "\n".join([doc.page_content for doc in relevant_company_docs])
            
            # Enhanced LLM prompt for structured analysis
            analysis_prompt = f"""
You are a compliance expert. Analyze the company's documentation against {regulation_type} requirements.

REGULATION REQUIREMENTS:
{reg_context}

COMPANY DOCUMENTATION:
{company_doc_context}

COMPANY DESCRIPTION: {agent_instance.company_context.get('description', 'Not provided')}

Analyze the compliance status and return a JSON response with the following structure. **You must ALWAYS return the full JSON structure, even if all values are zero or empty. If you cannot find any issues, return zeros and empty lists, but never omit any field. Return ONLY the JSON, no extra text, no explanations, no markdown.**

{{
  "regulation": "{regulation_type}",
  "total_requirements": <number>,
  "compliant_count": <number>,
  "non_compliant_count": <number>,
  "warnings_count": <number>,
  "issues": [
    {{
      "id": <unique_id>,
      "title": "<issue_title>",
      "status": "success|warning|error",
      "description": "<detailed_description>",
      "suggestion": "<AI_generated_recommendation>",
      "regulation": "{regulation_type}",
      "section": "<regulation_section>",
      "severity": "critical|high|medium|low",
      "risk_level": "high|medium|low"
    }}
  ],
  "summary": {{
    "overall_status": "compliant|partial|non_compliant",
    "critical_issues": <number>,
    "high_risk_issues": <number>,
    "medium_risk_issues": <number>,
    "low_risk_issues": <number>
  }}
}}

Focus on specific, actionable findings. Each issue should have:
- Clear title describing the compliance requirement
- Accurate status (success=compliant, warning=partial, error=non-compliant)
- Detailed description of the finding
- Specific recommendation for remediation
- Proper regulation section reference
- Appropriate severity and risk assessment

If you cannot find any issues, return an empty list for "issues" and zeros for all counts, but always return the full JSON structure. Return ONLY the JSON, no extra text.
"""
            
            analysis_result = agent_instance.llm.invoke(analysis_prompt)
            print('DEBUG: ibm/granite-3-2b-instruct output:', analysis_result)
            parsed_result = None
            try:
                cleaned = clean_json_string(analysis_result)
                parsed_result = json.loads(cleaned)
            except Exception as e1:
                print('DEBUG: Cleaned JSON parse failed:', e1)
                # Try to extract JSON using regex
                match = re.search(r'\{[\s\S]*\}', analysis_result)
                if match:
                    try:
                        cleaned = clean_json_string(match.group(0))
                        parsed_result = json.loads(cleaned)
                    except Exception as e2:
                        print('DEBUG: Regex JSON extraction failed:', e2)
                        parsed_result = None
                else:
                    print('DEBUG: No JSON block found in LLM output')
            if parsed_result:
                agent_instance.compliance_findings[regulation_type] = parsed_result
                return f"Completed {regulation_type} gap analysis. Found {parsed_result.get('non_compliant_count', 0)} non-compliant issues and {parsed_result.get('warnings_count', 0)} warnings."
            else:
                # Fallback: always return a valid JSON structure with error field
                fallback_result = {
                    "regulation": regulation_type,
                    "total_requirements": 0,
                    "compliant_count": 0,
                    "non_compliant_count": 0,
                    "warnings_count": 0,
                    "issues": [],
                    "summary": {
                        "overall_status": "unknown",
                        "critical_issues": 0,
                        "high_risk_issues": 0,
                        "medium_risk_issues": 0,
                        "low_risk_issues": 0
                    },
                    "error": "LLM did not return valid JSON. Raw output: " + analysis_result[:500]
                }
                agent_instance.compliance_findings[regulation_type] = fallback_result
                return f"Completed {regulation_type} analysis. Raw results could not be parsed as JSON."
        
        except Exception as e:
            # Fallback: always return a valid JSON structure with error field
            fallback_result = {
                "regulation": regulation_type,
                "total_requirements": 0,
                "compliant_count": 0,
                "non_compliant_count": 0,
                "warnings_count": 0,
                "issues": [],
                "summary": {
                    "overall_status": "unknown",
                    "critical_issues": 0,
                    "high_risk_issues": 0,
                    "medium_risk_issues": 0,
                    "low_risk_issues": 0
                },
                "error": f"Exception in compliance_gap_analysis: {str(e)}"
            }
            agent_instance.compliance_findings[regulation_type] = fallback_result
            return f"Error in compliance gap analysis: {str(e)}"

    @tool(return_direct=True)
    def generate_compliance_report() -> str:
        """Generate comprehensive compliance assessment report from all analyses."""
        if not agent_instance.compliance_findings:
            return "No compliance analysis data available. Please run gap analysis for at least one regulation first."
        
        try:
            # Compile report
            findings_summary = ""
            for regulation, analysis in agent_instance.compliance_findings.items():
                if isinstance(analysis, dict) and 'raw_analysis' in analysis:
                    findings_summary += f"\n\n=== {regulation} ANALYSIS ===\n{analysis['raw_analysis']}"
                else:
                    findings_summary += f"\n\n=== {regulation} ANALYSIS ===\n{analysis}"
            
            report_prompt = f"""
Generate a professional compliance assessment report based on the following analysis:

COMPANY: {agent_instance.company_context.get('description', 'Company under assessment')}
DOCUMENT CHUNKS ANALYZED: {agent_instance.company_context.get('document_chunks', 'Not specified')}

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
            
            final_report = agent_instance.llm.invoke(report_prompt)
            
            # Add metadata to report
            metadata_header = f"""
COMPLIANCE ASSESSMENT REPORT
Generated: {agent_instance.company_context.get('description', 'Unknown Company')}
Regulations Analyzed: {', '.join(agent_instance.compliance_findings.keys())}
Document Chunks: {agent_instance.company_context.get('document_chunks', 'Not specified')}
Analysis Date: Auto-generated

{'='*60}
"""
            
            return metadata_header + final_report
            
        except Exception as e:
            return f"Error generating compliance report: {str(e)}"

    return [ingest_company_documents, process_uploaded_files, compliance_gap_analysis, generate_compliance_report]

def clean_json_string(s):
    # Remove JS-style comments
    s = re.sub(r'//.*', '', s)
    # Remove trailing commas before closing brackets/braces
    s = re.sub(r',([ \t\r\n]*[}}\]])', r'\1', s)
    return s
