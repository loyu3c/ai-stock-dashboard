import os
import sys
import gspread
from config import Config

def main():
    print("--- Google Sheets Connection Test ---")
    
    # Check if service account file exists
    if not os.path.exists(Config.GOOGLE_SERVICE_ACCOUNT_FILE):
        print(f"❌ Error: Service account file not found: {Config.GOOGLE_SERVICE_ACCOUNT_FILE}")
        print("Please ensure 'service_account.json' is placed in the project root.")
        return

    try:
        # Attempt authentication
        gc = gspread.service_account(filename=Config.GOOGLE_SERVICE_ACCOUNT_FILE)
        print("✅ Authentication successful!")
        
        # Attempt to open sheet if URL is provided
        if Config.GOOGLE_SHEET_URL:
            print(f"Attempting to open sheet: {Config.GOOGLE_SHEET_URL}")
            try:
                sh = gc.open_by_url(Config.GOOGLE_SHEET_URL)
                print(f"✅ Successfully Connected to Sheet: '{sh.title}'")
            except gspread.exceptions.SpreadsheetNotFound:
                print("❌ Error: Spreadsheet not found. Please check the URL.")
            except Exception as e:
                print(f"❌ Error opening sheet: {e}")
                print("Tip: Did you share the sheet with the service account email?")
        else:
            print("ℹ️ GOOGLE_SHEET_URL not set in configuration. Skipping sheet access test.")
            print("To test a specific sheet, set GOOGLE_SHEET_URL in your .env or config.py")

    except Exception as e:
        print(f"❌ Authentication failed: {e}")

if __name__ == "__main__":
    main()
