import shioaji as sj
from config import Config
import os

def main():
    print("--- Shioaji API Connection Test ---")
    
    if not Config.check_required():
        print("❌ Missing required environment variables. Please check .env file.")
        return

    api = sj.Shioaji(simulation=True)
    
    try:
        print(f"Attempting to login...")
        # Check if PFX file exists
        if not os.path.exists(Config.SHIOAJI_PFX_PATH):
             print(f"❌ Error: PFX file not found at: {Config.SHIOAJI_PFX_PATH}")
             return

        api.login(
            api_key=Config.SHIOAJI_API_KEY,
            secret_key=Config.SHIOAJI_SECRET_KEY,
            contracts_cb=lambda security_type: print(f"✅ Contracts loaded: {security_type}")
        )
        print("✅ Login API Call Successful!")
        
        # Activate CA
        # print("Attempting to activate CA...")
        # api.activate_ca(
        #     ca_path=Config.SHIOAJI_PFX_PATH,
        #     ca_passwd=Config.SHIOAJI_PFX_PASSWORD,
        #     person_id=api.stock_account.person_id
        # )
        # print("✅ CA Activated!")

        # Test Data Fetch (TSMC 2330)
        print("Fetching TSMC (2330) data...")
        contract = api.Contracts.Stocks["2330"]
        snapshots = api.snapshots([contract])
        print(f"✅ Data Received: {snapshots}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        api.logout()
        print("Logged out.")

if __name__ == "__main__":
    main()
