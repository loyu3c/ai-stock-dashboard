import shioaji as sj
from config import Config

class ShioajiLogin:
    _api_instance = None

    @classmethod
    def get_api(cls):
        """
        Returns a singleton instance of the logged-in Shioaji API.
        """
        if cls._api_instance is None:
            cls._login()
        return cls._api_instance

    @classmethod
    def _login(cls):
        print("Creating Shioaji API instance (Simulation Mode)...")
        # Force simulation=True based on testing results
        cls._api_instance = sj.Shioaji(simulation=True)
        
        try:
            cls._api_instance.login(
                api_key=Config.SHIOAJI_API_KEY,
                secret_key=Config.SHIOAJI_SECRET_KEY,
                contracts_cb=lambda security_type: print(f"✅ [Shioaji] Contracts loaded: {security_type}")
            )
            print("✅ [Shioaji] Login successful.")
            
            # CA Activation is skipped for now as per user instruction/testing
            # cls._activate_ca() 

        except Exception as e:
            print(f"❌ [Shioaji] Login failed: {e}")
            raise e

    @classmethod
    def _activate_ca(cls):
        if not Config.SHIOAJI_PFX_PATH or not Config.SHIOAJI_PFX_PASSWORD:
            print("⚠️ [Shioaji] CA credentials missing, skipping activation.")
            return

        try:
            cls._api_instance.activate_ca(
                ca_path=Config.SHIOAJI_PFX_PATH,
                ca_passwd=Config.SHIOAJI_PFX_PASSWORD,
                person_id=cls._api_instance.stock_account.person_id
            )
            print("✅ [Shioaji] CA Activated.")
        except Exception as e:
            print(f"⚠️ [Shioaji] CA Activation failed (Ignored in Simulation): {e}")

    @classmethod
    def logout(cls):
        if cls._api_instance:
            cls._api_instance.logout()
            print("✅ [Shioaji] Logged out.")
            cls._api_instance = None
