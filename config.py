import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Shioaji (Sinopac)
    SHIOAJI_API_KEY = os.getenv("SHIOAJI_API_KEY")
    SHIOAJI_SECRET_KEY = os.getenv("SHIOAJI_SECRET_KEY")
    SHIOAJI_PFX_PATH = os.getenv("SHIOAJI_PFX_PATH")
    SHIOAJI_PFX_PASSWORD = os.getenv("SHIOAJI_PFX_PASSWORD")
    
    # Google Sheets
    GOOGLE_SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "service_account.json")
    GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")
    
    # Line Messaging API
    LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    LINE_USER_ID = os.getenv("LINE_USER_ID")

    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")

    @classmethod
    def check_required(cls):
        """Check if essential variables are set"""
        missing = []
        if not cls.SHIOAJI_API_KEY: missing.append("SHIOAJI_API_KEY")
        if not cls.SHIOAJI_SECRET_KEY: missing.append("SHIOAJI_SECRET_KEY")
        
        if missing:
            print(f"Warning: Missing environment variables: {', '.join(missing)}")
        return len(missing) == 0
