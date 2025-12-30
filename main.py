import pandas as pd
from datetime import datetime
from market_scanner import MarketScanner
from sheet_manager import SheetManager
from line_notifier import LineNotifier

def main():
    print("=== 🚀 AI Stock Assistant Automation Started ===")
    
    # 1. Run Market Scan
    print("\n[Step 1] Scanning Market...")
    scanner = MarketScanner() # Default top weighted stocks
    df = scanner.run_scan()
    
    if df.empty:
        print("⚠️ No data found or market closed.")
        return

    # 2. Update Google Sheets
    print("\n[Step 2] Updating Google Sheets...")
    sheet_manager = SheetManager()
    sheet_manager.update_daily_report(df)
    
    # 3. Send Line Notification
    print("\n[Step 3] Sending Line Notification...")
    notifier = LineNotifier()
    
    # Construct Message
    today = datetime.now().strftime("%Y-%m-%d")
    green_stocks = df[df['Signal'] == '🟢']['Stock'].tolist()
    red_stocks = df[df['Signal'] == '🔴']['Stock'].tolist()
    
    msg = f"📊 AI選股日報 ({today})\n\n"
    
    if green_stocks:
        msg += f"🟢 綠燈 (買進關注): {', '.join(green_stocks)}\n"
    else:
        msg += "🟢 綠燈: 無\n"
        
    if red_stocks:
        msg += f"🔴 紅燈 (留意賣點): {', '.join(red_stocks)}\n"
        
    msg += f"\n🟡 其餘 {len(df) - len(green_stocks) - len(red_stocks)} 檔為黃燈觀望。\n"
    msg += "\n📈 完整報表已更新至 Google Sheets。"
    
    notifier.send_message(msg)
    
    print("\n=== ✅ All Tasks Completed Successfully ===")

if __name__ == "__main__":
    main()
