"""
Main entry point for the Compliance RAG Agent API
"""

from config import Config
from api import create_app


def main():
    """Main function to run the Flask API application."""
    print("""
=== COMPLIANCE RAG AGENT API ===

Starting API server for compliance document analysis...

API ENDPOINTS:
- POST /setup_ingestion - Setup document ingestion with company description
- POST /upload - Upload compliance documents
- POST /process_files - Process uploaded files
- POST /analyze/<regulation_type> - Analyze compliance (GDPR, NIST, HIPAA, ISO27001)
- POST /analyze_gdpr - Analyze GDPR compliance (backward compatibility)
- POST /generate_report - Generate compliance report
- GET /status - Get current analysis status
- GET /health - Health check
- GET /available_regulations - List available regulations
- POST /reset - Reset analysis session

WORKFLOW:
1. POST /setup_ingestion with company description
2. POST /upload with compliance documents
3. POST /process_files to process uploaded files
4. POST /analyze/<regulation> for each regulation
5. POST /generate_report for final report

The API will be available at: http://localhost:5000

Press Ctrl+C to stop the server.
""")

    # Initialize configuration
    config = Config()
    
    # Create Flask app
    app = create_app(config)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)


if __name__ == "__main__":
    main()
