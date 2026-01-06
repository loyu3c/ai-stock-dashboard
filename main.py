from datetime import datetime
from market_scanner import MarketScanner
from db_manager import DBManager
from line_notifier import LineNotifier

def main():
    print("=== 🚀 AI Stock Assistant Automation Started ===")
    
    # 1. Run Market Scan
    print("\n[Step 1] Scanning Market...")
    
    # Initialize DBManager
    db_manager = DBManager()
    stock_list = db_manager.fetch_stock_list()
    config = db_manager.fetch_strategy_config()
    
    if not stock_list:
        print("⚠️ Warning: Stock list is empty. Check DB 'stocks' table (or use Settings page).")
    
    scanner = MarketScanner(stock_list=stock_list, config=config)
    df = scanner.run_scan()
    
    if df.empty:
        print("⚠️ No data found or market closed.")
        return

    # 2. Update Database
    print("\n[Step 2] Updating Database (SQLite)...")
    db_manager.save_analysis_result(df)
    
    # 3. Send Line Notification
    print("\n[Step 3] Sending Line Notification...")
    notifier = LineNotifier()
    
    # Construct Message
    today = datetime.now().strftime("%Y-%m-%d")
    
    msg = f"\n📊 AI選股日報 ({today})\n"
    
    # Green Light
    green_df = df[df['Signal'] == '🟢']
    if not green_df.empty:
        msg += "\n🟢 綠燈 (買進關注):\n"
        for _, row in green_df.iterrows():
            msg += f"{row['Name']}({row['Stock']}) - {row['Close']}\n"
    else:
        msg += "\n🟢 綠燈: 無\n"
        
    # Red Light
    red_df = df[df['Signal'] == '🔴']
    if not red_df.empty:
        msg += "\n🔴 紅燈 (留意賣點):\n"
        for _, row in red_df.iterrows():
            msg += f"{row['Name']}({row['Stock']}) - {row['Close']}\n"

    msg += f"\n🟡 其餘 {len(df) - len(green_df) - len(red_df)} 檔為黃燈觀望。\n"
    msg += "\n📈 完整報表已更新至 Dashboard / 資料庫。"
    
    notifier.send_message(msg)
    
    print("\n=== ✅ All Tasks Completed Successfully ===")

if __name__ == "__main__":
    main()
