from db_manager import DBManager
import pandas as pd

# 0050 Constituents (Fetched from WantGoo)
new_stocks = [
  {"code": "2330", "name": "台積電"},
  {"code": "2317", "name": "鴻海"},
  {"code": "2454", "name": "聯發科"},
  {"code": "2308", "name": "台達電"},
  {"code": "2382", "name": "廣達"},
  {"code": "2891", "name": "中信金"},
  {"code": "2881", "name": "富邦金"},
  {"code": "2882", "name": "國泰金"},
  {"code": "3711", "name": "日月光投控"},
  {"code": "2303", "name": "聯電"},
  {"code": "2345", "name": "智邦"},
  {"code": "2884", "name": "玉山金"},
  {"code": "2412", "name": "中華電"},
  {"code": "2886", "name": "兆豐金"},
  {"code": "2357", "name": "華碩"},
  {"code": "3231", "name": "緯創"},
  {"code": "2887", "name": "台新金"},
  {"code": "1216", "name": "統一"},
  {"code": "2885", "name": "元大金"},
  {"code": "6669", "name": "緯穎"},
  {"code": "2383", "name": "台光電"},
  {"code": "2301", "name": "光寶科"},
  {"code": "2892", "name": "第一金"},
  {"code": "3017", "name": "奇鋐"},
  {"code": "2890", "name": "永豐金"},
  {"code": "2880", "name": "華南金"},
  {"code": "3661", "name": "世芯-KY"},
  {"code": "2379", "name": "瑞昱"},
  {"code": "2327", "name": "國巨"},
  {"code": "5880", "name": "合庫金"},
  {"code": "3034", "name": "聯詠"},
  {"code": "2883", "name": "凱基金"},
  {"code": "3008", "name": "大立光"},
  {"code": "2002", "name": "中鋼"},
  {"code": "1303", "name": "南亞"},
  {"code": "2603", "name": "長榮"},
  {"code": "6919", "name": "康霈"},
  {"code": "2059", "name": "川湖"},
  {"code": "5871", "name": "中租-KY"},
  {"code": "2207", "name": "和泰車"},
  {"code": "5876", "name": "上海商銀"},
  {"code": "1301", "name": "台塑"},
  {"code": "3045", "name": "台灣大"},
  {"code": "4904", "name": "遠傳"},
  {"code": "2395", "name": "研華"},
  {"code": "4938", "name": "和碩"},
  {"code": "2912", "name": "統一超"},
  {"code": "2615", "name": "萬海"},
  {"code": "2609", "name": "陽明"},
  {"code": "6505", "name": "台塑化"},
  {"code": "6446", "name": "藥華藥"}
]

def add_0050():
    db = DBManager()
    
    # 1. Clear existing stocks
    print("🗑️ Clearing all existing stocks...")
    import sqlite3
    import os
    
    # Use DBManager's path logic if possible, but it's simple enough
    db_path = os.path.join("data", "stock_data.db")
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM stocks")
        conn.commit()
    print("✅ Stock list cleared.")

    # 2. Prepare new list
    final_list = []
    for stock in new_stocks:
        final_list.append({
            "Stock": str(stock['code']),
            "Name": stock['name'],
            "Enabled": "TRUE",
            "Memo": "0050成分股"
        })
            
    # 3. Save back
    print(f"Adding {len(final_list)} new stocks from 0050 list...")
    db.save_stock_list(final_list)
    print("✅ Successfully updated stock list in SQLite.")

if __name__ == "__main__":
    add_0050()
