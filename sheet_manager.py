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

if __name__ == "__main__":
    # Test Run
    import os
    if os.path.exists("daily_report.csv"):
        df = pd.read_csv("daily_report.csv")
        manager = SheetManager()
        manager.update_daily_report(df)
    else:
        print("Please run market_scanner.py first to generate a report.")
