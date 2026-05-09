"""
Configuration file for Village Gentle - Agricultural AI Platform
Loads environment variables securely
"""

import os
from dotenv import load_dotenv
import streamlit as st

# Version for deployment verification
CONFIG_VERSION = "1.0.2-safe-secrets"

# Load environment variables from .env file
load_dotenv()

def get_secret(key, default=''):
    """
    Safely get a secret from environment variables or Streamlit secrets.
    Prioritizes environment variables (useful for local .env and Render/Cloud env vars).
    Falls back to Streamlit secrets only if available and not throwing errors.
    """
    # 1. Try environment variable first (standard for most deployments)
    val = os.getenv(key)
    if val is not None and val != '':
        return val
    
    # 2. Try Streamlit secrets safely
    # We check for the existence of the secrets file to avoid triggering a FileNotFoundError
    # when accessing st.secrets on platforms like Render.
    secrets_file_exists = os.path.exists(".streamlit/secrets.toml") or \
                          os.path.exists(os.path.expanduser("~/.streamlit/secrets.toml"))
    
    if secrets_file_exists:
        try:
            # Only access st.secrets if we think it's safe
            return st.secrets.get(key, default)
        except Exception:
            # Fallback if something still goes wrong
            pass
        
    return default

class Config:
    """Configuration class to manage all API keys and settings"""
    
    def __init__(self):
        print(f"Initializing Village Gentle Config v{CONFIG_VERSION}")
        
        # AI APIs
        self.GROQ_API_KEY = get_secret('GROQ_API_KEY')
        self.MISTRAL_API_KEY = get_secret('MISTRAL_API_KEY')
        self.ASSEMBLYAI_API_KEY = get_secret('ASSEMBLYAI_API_KEY')
        
        # Google APIs
        self.GOOGLE_API_KEY = get_secret('GOOGLE_API_KEY')
        self.GOOGLE_CSE_ID = get_secret('GOOGLE_CSE_ID')
        self.YOUTUBE_API_KEY = get_secret('YOUTUBE_API_KEY')
        
        # Search APIs
        self.SERPAPI_KEY = get_secret('SERPAPI_KEY')
        
        # Location APIs
        self.ORS_API_KEY = get_secret('ORS_API_KEY')
        self.WINDY_API_KEY = get_secret('WINDY_API_KEY')
        
        # Plant/Pest Detection
        self.KINDWISE_API_KEY = get_secret('KINDWISE_API_KEY')
        
        # Nutrition API
        self.NUTRITIONIX_APP_ID = get_secret('NUTRITIONIX_APP_ID')
        self.NUTRITIONIX_APP_KEY = get_secret('NUTRITIONIX_APP_KEY')
        
        # Hugging Face
        self.HF_TOKEN = get_secret('HF_TOKEN')
        
        # Database
        self.MONGODB_URI = get_secret('MONGODB_URI')
        
        # Blockchain (Optional)
        self.WEB3_PROVIDER_URL = get_secret('WEB3_PROVIDER_URL')
        self.BLOCKCHAIN_PRIVATE_KEY = get_secret('BLOCKCHAIN_PRIVATE_KEY')
        self.BLOCKCHAIN_WALLET_ADDRESS = get_secret('BLOCKCHAIN_WALLET_ADDRESS')
        self.BLOCKCHAIN_ENABLED = get_secret('BLOCKCHAIN_ENABLED', 'false').lower() == 'true'
        
        # API Endpoints
        self.GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
        self.MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"
        self.ASSEMBLYAI_UPLOAD_URL = "https://api.assemblyai.com/v2/upload"
        self.ASSEMBLYAI_TRANSCRIPT_URL = "https://api.assemblyai.com/v2/transcript"
    
    def validate_keys(self):
        """Validate that required API keys are present"""
        required_keys = [
            'GROQ_API_KEY', 'MONGODB_URI'
        ]
        
        missing_keys = []
        for key in required_keys:
            if not getattr(self, key):
                missing_keys.append(key)
        
        if missing_keys:
            st.error(f"Missing required API keys: {', '.join(missing_keys)}")
            st.info("Please ensure you have set the Environment Variables in your Render dashboard.")
            return False
        return True

# Create a global config instance
config = Config()