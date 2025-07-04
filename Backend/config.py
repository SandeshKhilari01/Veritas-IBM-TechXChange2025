"""
Configuration module for Compliance RAG Agent
"""

import os
from ibm_granite_community.notebook_utils import get_env_var

class Config:
    """Configuration class for the Compliance RAG Agent."""
    
    def __init__(self):
        self.setup_credentials()
        self.setup_app_config()
    
    def setup_credentials(self):
        """Set up Watson AI and AstraDB credentials from environment variables."""
        self.watsonx_credentials = {
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
    
    def setup_app_config(self):
        """Set up Flask application configuration."""
        self.max_content_length = 50 * 1024 * 1024  # 50MB max file size
        self.upload_folder = 'uploads'
        self.secret_key = 'compliance-rag-secret-key'
        self.allowed_extensions = {'pdf', 'docx', 'txt', 'md'}
        
        # Create uploads directory if it doesn't exist
        os.makedirs(self.upload_folder, exist_ok=True)
        
        # Set USER_AGENT to avoid warning
        os.environ["USER_AGENT"] = "compliance-rag-agent/1.0"
