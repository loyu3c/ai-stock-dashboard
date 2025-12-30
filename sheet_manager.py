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
        full_config = self.fetch_strategy_config_full()
        # Convert list back to simple dict for backward compatibility
        simple_config = {item['Parameter']: item['Value'] for item in full_config}
        return simple_config

    def fetch_strategy_config_full(self) -> list:
        """
        Fetches the 'Strategy Config' worksheet and returns a list of detailed objects.
        Also automatically populates Chinese descriptions if missing.
        Returns:
            list: [{ 'Parameter': 'MA_SHORT_DAYS', 'Value': 10, 'Description': '...' }, ...]
        """
        if not self.sh:
            return []

        DEFAULT_DESCRIPTIONS = {
            "MA_SHORT_DAYS": "短期移動平均線天數 (例如 10 日線)",
            "MA_LONG_DAYS": "長期移動平均線天數 (例如 20 日線)",
            "RSI_THRESHOLD": "RSI 相關指標的判斷門檻",
            "KD_THRESHOLD": "KD 隨機指標的判斷門檻",
            "MACD_FAST": "MACD 快速移動平均線天數 (通常為 12)",
            "MACD_SLOW": "MACD 慢速移動平均線天數 (通常為 26)",
            "MACD_SIGNAL": "MACD 訊號線天數 (通常為 9)"
        }

        try:
            ws = self.sh.worksheet("Strategy Config")
            records = ws.get_all_records()
            
            # If sheet is empty or headers missing, it might crash get_all_records or return empty
            # But assuming it's initialized.
            
            config_list = []
            updates_needed = False

            # We want to ensure all keys in DEFAULT_DESCRIPTIONS exist or at least what is in the sheet
            # Let's trust the sheet as the source of truth for keys, but add descriptions.
            
            # If records are empty but we have defaults, maybe we should init the sheet? 
            # For now, let's just process what is there.
            
            for r in records:
                key = r.get('Parameter')
                val = r.get('Value')
                desc = r.get('Description', '')

                if key:
                    # Type conversion
                    try:
                        if isinstance(val, str) and '.' in val:
                            val = float(val)
                        else:
                            val = int(val)
                    except ValueError:
                        pass 

                    # Populate Description if missing
                    if not desc and key in DEFAULT_DESCRIPTIONS:
                        desc = DEFAULT_DESCRIPTIONS[key]
                        # We should update the sheet back later or just return it for display?
                        # Ideally update the sheet so it persists. 
                        # But writing back line-by-line is slow. 
                        # Let's collect data and update if we found missing descriptions.
                        updates_needed = True

                    config_list.append({
                        "Parameter": key,
                        "Value": val,
                        "Description": desc
                    })
            
            if updates_needed:
                print("ℹ️ Updating missing descriptions in Google Sheet...")
                self._update_whole_strategy_sheet(config_list)

            print(f"✅ Fetched {len(config_list)} detailed strategy parameters.")
            return config_list

        except gspread.exceptions.WorksheetNotFound:
            print("❌ 'Strategy Config' sheet not found.")
            return []
        except Exception as e:
            print(f"❌ Failed to fetch config full: {e}")
            return []

    def _update_whole_strategy_sheet(self, config_list: list):
        """Helper to overwrite the strategy sheet with new list."""
        try:
            ws = self.sh.worksheet("Strategy Config")
            ws.clear()
            
            df = pd.DataFrame(config_list)
            desired_columns = ["Parameter", "Value", "Description"]
            # Ensure columns exist
            for col in desired_columns:
                if col not in df.columns:
                    df[col] = ""
            
            df = df[desired_columns]
            data = [df.columns.values.tolist()] + df.values.tolist()
            ws.update(data)
        except Exception as e:
            print(f"❌ Failed to update strategy sheet: {e}")

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
            # We fetch existing detailed config first to preserve descriptions
            current_detailed = self.fetch_strategy_config_full()
            
            # Map existing configs by Parameter for easy update
            config_map = {item['Parameter']: item for item in current_detailed}
            
            # Update values from input config_dict
            new_list = []
            full_keys = set(config_map.keys()) | set(config_dict.keys())
            
            # We want to preserve order if possible, or just append new ones. 
            # Let's iterate over known keys first + any new ones.
            # Ideally we stick to what is in existing list to keep order.
            
            # Create a new list based on current_detailed order
            processed_keys = set()
            for item in current_detailed:
                key = item['Parameter']
                if key in config_dict:
                    item['Value'] = config_dict[key]
                new_list.append(item)
                processed_keys.add(key)
                
            # Add any NEW keys from config_dict that weren't in detailed list
            for key, val in config_dict.items():
                if key not in processed_keys:
                    new_list.append({
                        "Parameter": key, 
                        "Value": val, 
                        "Description": ""
                    })
            
            self._update_whole_strategy_sheet(new_list)
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
