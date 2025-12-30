import gspread
import pandas as pd
from config import Config

class SheetManager:
    def __init__(self):
        self.sh = None
        
        if not Config.GOOGLE_SHEET_URL or "your_sheet_id" in Config.GOOGLE_SHEET_URL:
            print("⚠️ Warning: GOOGLE_SHEET_URL not set or valid in .env")
            return

        try:
            self.gc = gspread.service_account(filename=Config.GOOGLE_SERVICE_ACCOUNT_FILE)
            self.sh = self.gc.open_by_url(Config.GOOGLE_SHEET_URL)
            print(f"✅ Connected to Google Sheet: {self.sh.title}")
        except Exception as e:
            print(f"❌ Failed to connect to Google Sheet: {e}")
            self.sheet = None

    def update_daily_report(self, df: pd.DataFrame, worksheet_name: str = "Daily Report"):
        """
        Updates the specified worksheet with the DataFrame content.
        Creates the worksheet if it doesn't exist.
        """
        if not self.sh:
            print("❌ No active sheet connection. Please check GOOGLE_SHEET_URL in .env")
            return

        try:
            # Select or Create Worksheet
            try:
                ws = self.sh.worksheet(worksheet_name)
                ws.clear()
            except gspread.exceptions.WorksheetNotFound:
                ws = self.sh.add_worksheet(title=worksheet_name, rows=100, cols=20)
                print(f"Created new worksheet: {worksheet_name}")

            # Prepare Data
            # Convert DataFrame to list of lists (including header)
            data = [df.columns.values.tolist()] + df.values.tolist()
            
            # Update Sheet
            ws.update(data)
            print(f"✅ Updated '{worksheet_name}' with {len(df)} rows.")
            
            # Formatting (Freeze Top Row)
            try:
                ws.freeze(rows=1)
            except:
                pass # Ignore if freeze fails
            
            self._apply_conditional_formatting(ws, len(df))

        except Exception as e:
            print(f"❌ Failed to update sheet: {e}")

    def _apply_conditional_formatting(self, ws, row_count):
        """
        Applies basic conditional formatting for Signals.
        """
        # Define ranges (Assuming Signal is in Column D, i.e., index 3 -> Col D)
        # Note: A1 notation. Column D is 4th column.
        
        # We can implement specific API calls for color rules later.
        # For now, we rely on the emoji characters (🔴, 🟢, 🟡) which are visually distinct.
        pass

    def fetch_stock_list(self) -> list:
        """
        Fetches the 'Stock List' worksheet and returns a list of enabled stock codes.
        Returns:
            list: List of stock codes (str) e.g., ['2330', '2317']
        """
        if not self.sh:
            return []

        try:
            ws = self.sh.worksheet("Stock List")
            records = ws.get_all_records()
            
            # Filter Enabled == 'TRUE' (string comparison from GSheets)
            # Handle case sensitivity just in case
            enabled_stocks = [
                str(r['Stock']) for r in records 
                if str(r.get('Enabled', '')).upper() == 'TRUE'
            ]
            print(f"✅ Fetched {len(enabled_stocks)} enabled stocks from Google Sheet.")
            return enabled_stocks
        except gspread.exceptions.WorksheetNotFound:
            print("❌ 'Stock List' sheet not found.")
            return []
        except Exception as e:
            print(f"❌ Failed to fetch stock list: {e}")
            return []

    def fetch_strategy_config(self) -> dict:
        """
        Fetches the 'Strategy Config' worksheet and returns a parameter dictionary.
        Returns:
            dict: { 'MA_SHORT_DAYS': 10, ... }
        """
        if not self.sh:
            return {}

        try:
            ws = self.sh.worksheet("Strategy Config")
            records = ws.get_all_records()
            
            config = {}
            for r in records:
                key = r.get('Parameter')
                val = r.get('Value')
                if key:
                    # Try to convert to int/float if possible
                    try:
                        if isinstance(val, str) and '.' in val:
                            val = float(val)
                        else:
                            val = int(val)
                    except ValueError:
                        pass # Keep as string
                    config[key] = val
            
            print(f"✅ Fetched {len(config)} strategy parameters.")
            return config
        except gspread.exceptions.WorksheetNotFound:
            print("❌ 'Strategy Config' sheet not found. Using defaults.")
            return {}
        except Exception as e:
            print(f"❌ Failed to fetch config: {e}")
            return {}

    def save_stock_list(self, stock_list: list) -> bool:
        """
        Saves the list of stock dictionaries to 'Stock List' sheet.
        Args:
            stock_list: List of dicts e.g., [{'Stock': '2330', 'Name': '台積電', 'Enabled': 'TRUE', ...}]
        """
        if not self.sh:
            return False

        try:
            ws = self.sh.worksheet("Stock List")
            ws.clear()
            
            if not stock_list:
                print("⚠️ Stock list is empty, clearing sheet.")
                return True

            # Convert list of dicts to DataFrame for easy handling
            df = pd.DataFrame(stock_list)
            
            # Ensure columns are in a specific order if desired, or just dump
            # We want to keep the structure: Stock, Name, Enabled, Memo
            desired_columns = ["Stock", "Name", "Enabled", "Memo"]
            # Add missing columns if any
            for col in desired_columns:
                if col not in df.columns:
                    df[col] = ""
            
            # Reorder
            df = df[desired_columns]
            
            # Update
            data = [df.columns.values.tolist()] + df.values.tolist()
            ws.update(data)
            print(f"✅ Saved {len(stock_list)} stocks to Google Sheet.")
            return True
        except Exception as e:
            print(f"❌ Failed to save stock list: {e}")
            return False

    def save_strategy_config(self, config_dict: dict) -> bool:
        """
        Saves the config dictionary to 'Strategy Config' sheet.
        Args:
            config_dict: Dict e.g., {'MA_SHORT_DAYS': 10, ...}
        """
        if not self.sh:
            return False

        try:
            ws = self.sh.worksheet("Strategy Config")
            ws.clear()
            
            # Convert dict back to list of dicts structure: Parameter, Value, Description
            # We need to preserve descriptions if possible. 
            # Ideally, the frontend sends back the full object including description, 
            # OR we fetch existing to keep descriptions. 
            # For simplicity, let's assume the frontend sends full objects OR we just write what we have.
            # Strategy: The input here is likely a simple key-value dict from the API.
            # We should probably fetch the existing sheet first to preserve Descriptions.
            
            current_records = ws.get_all_records()
            record_map = {r['Parameter']: r.get('Description', '') for r in current_records}
            
            new_data = []
            for key, val in config_dict.items():
                desc = record_map.get(key, "") # Preserve description or empty
                new_data.append({"Parameter": key, "Value": val, "Description": desc})
            
            if not new_data:
                 print("⚠️ Config is empty.")
                 return True
                 
            df = pd.DataFrame(new_data)
            desired_columns = ["Parameter", "Value", "Description"]
            df = df[desired_columns]
            
            data = [df.columns.values.tolist()] + df.values.tolist()
            ws.update(data)
            print(f"✅ Saved strategy config to Google Sheet.")
            return True
        except Exception as e:
            print(f"❌ Failed to save strategy config: {e}")
            return False

if __name__ == "__main__":
    # Test Run
    import os
    if os.path.exists("daily_report.csv"):
        df = pd.read_csv("daily_report.csv")
        manager = SheetManager()
        manager.update_daily_report(df)
    else:
        print("Please run market_scanner.py first to generate a report.")
