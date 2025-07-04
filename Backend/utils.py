"""
Utility functions for the Compliance RAG Agent
"""

import os
import tempfile
from typing import List
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document


def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def handle_agent_error(error: Exception, operation: str) -> str:
    """Handle agent errors gracefully."""
    error_msg = str(error)
    if "OUTPUT_PARSING_FAILURE" in error_msg:
        return f"Agent parsing error during {operation}. Please try again."
    elif "max_iterations" in error_msg:
        return f"Agent reached maximum iterations during {operation}. Please try a simpler request."
    else:
        return f"Error during {operation}: {error_msg}"


def process_files_to_documents(file_paths: List[str]) -> List[Document]:
    """Process uploaded files into document chunks.
    
    Args:
        file_paths: List of file paths to process
        
    Returns:
        List of processed document chunks
    """
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=300, chunk_overlap=50
    )
    
    documents = []
    
    print("Starting file processing...")
    
    for file_path in file_paths:
        try:
            filename = os.path.basename(file_path)
            print(f"Processing {filename}...")
            
            if filename.endswith('.pdf'):
                # Process PDF file directly
                loader = PyPDFLoader(file_path)
                file_documents = loader.load()
            
            elif filename.endswith('.txt') or filename.endswith('.md'):
                # Read text file
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                file_documents = [Document(
                    page_content=file_content, 
                    metadata={'source': filename, 'type': 'text'}
                )]
            
            elif filename.endswith('.docx'):
                # Process DOCX file directly
                loader = Docx2txtLoader(file_path)
                file_documents = loader.load()
            
            else:
                print(f"Unsupported file type: {filename}")
                continue
            
            # Split documents into chunks
            doc_splits = text_splitter.split_documents(file_documents)
            
            # Add metadata
            for doc in doc_splits:
                doc.metadata['processed_file'] = filename
                doc.metadata['chunk_size'] = len(doc.page_content)
            
            documents.extend(doc_splits)
            
            print(f"✓ Processed {filename}: {len(doc_splits)} chunks")
            
        except Exception as e:
            print(f"✗ Error processing {filename}: {str(e)}")
            continue
    
    print(f"\n📄 Total processed: {len(documents)} document chunks")
    return documents


def get_regulation_requirements(regulation_type: str) -> str:
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
