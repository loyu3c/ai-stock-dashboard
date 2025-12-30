import gspread
import pandas as pd
from config import Config
from sheet_manager import SheetManager

def init_sheets():
    print("🚀 Initializing Google Sheets Configuration...")
    
    manager = SheetManager()
    if not manager.sh:
        print("❌ Could not connect to Google Sheet.")
        return

    # 1. Initialize Stock List
    stock_list_data = [
        {"Stock": "2330", "Name": "台積電", "Enabled": "TRUE", "Memo": "權值股"},
        {"Stock": "2317", "Name": "鴻海", "Enabled": "TRUE", "Memo": "AI伺服器"},
        {"Stock": "2454", "Name": "聯發科", "Enabled": "TRUE", "Memo": "IC設計"},
        {"Stock": "2308", "Name": "台達電", "Enabled": "TRUE", "Memo": "電源供應"},
        {"Stock": "2303", "Name": "聯電", "Enabled": "TRUE", "Memo": "成熟製程"},
    ]
    _create_if_not_exists(manager.sh, "Stock List", stock_list_data)

    # 2. Initialize Strategy Config
    config_data = [
        {"Parameter": "MA_SHORT_DAYS", "Value": 10, "Description": "短均線天數 (跌破賣出)"},
        {"Parameter": "MA_LONG_DAYS", "Value": 20, "Description": "長均線天數 (趨勢判斷)"},
        {"Parameter": "RSI_THRESHOLD", "Value": 80, "Description": "RSI 過熱標準"},
        {"Parameter": "KD_THRESHOLD", "Value": 50, "Description": "KD 黃金交叉位階上限"},
        {"Parameter": "MACD_FAST", "Value": 12, "Description": "MACD 快線"},
        {"Parameter": "MACD_SLOW", "Value": 26, "Description": "MACD 慢線"},
        {"Parameter": "MACD_SIGNAL", "Value": 9, "Description": "MACD 訊號線"},
    ]
    _create_if_not_exists(manager.sh, "Strategy Config", config_data)
    
    print("\n✅ Initialization Complete! Please check your Google Sheet.")

def _create_if_not_exists(sh, title, data):
    try:
        sh.worksheet(title)
        print(f"ℹ️ Sheet '{title}' already exists. Skipping.")
    except gspread.exceptions.WorksheetNotFound:
        print(f"✨ Creating '{title}'...")
        ws = sh.add_worksheet(title=title, rows=100, cols=10)
        df = pd.DataFrame(data)
        # Convert to list of lists with header
        update_data = [df.columns.values.tolist()] + df.values.tolist()
        ws.update(update_data)
        print(f"   Populated '{title}' with {len(data)} rows.")

if __name__ == "__main__":
    init_sheets()
