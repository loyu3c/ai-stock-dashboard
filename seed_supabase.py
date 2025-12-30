from supabase_manager import SupabaseManager

def seed_data():
    mgr = SupabaseManager()
    if not mgr.client:
        print("❌ Cannot connect to Supabase.")
        return

    print("🌱 Seeding Supabase with default data...")

    # 1. Stocks
    stocks = [
        {"Stock": "2330", "Name": "台積電", "Enabled": "TRUE", "Memo": "權值股"},
        {"Stock": "2317", "Name": "鴻海", "Enabled": "TRUE", "Memo": "AI伺服器"},
        {"Stock": "2454", "Name": "聯發科", "Enabled": "TRUE", "Memo": "IC設計"},
        {"Stock": "2308", "Name": "台達電", "Enabled": "TRUE", "Memo": "電源供應"},
        {"Stock": "2303", "Name": "聯電", "Enabled": "TRUE", "Memo": "成熟製程"},
    ]
    mgr.save_stock_list(stocks)

    # 2. Strategy Params
    strategy = {
        "MA_SHORT_DAYS": 10,
        "MA_LONG_DAYS": 20,
        "RSI_THRESHOLD": 80,
        "KD_THRESHOLD": 50,
        "MACD_FAST": 12,
        "MACD_SLOW": 26,
        "MACD_SIGNAL": 9
    }
    # Note: save_strategy_config might overwrite descriptions if we aren't careful, 
    # but for initial seed it's fine. The SQL I gave earlier had defaults with descriptions.
    # Let's skip strategy seed if SQL already handled it (which it did).
    # But just in case SQL wasn't fully run or we want to be sure:
    mgr.save_strategy_config(strategy)
    
    print("✅ Seeding complete!")

if __name__ == "__main__":
    seed_data()
