import sqlite3
import json
import os
from datetime import datetime
import pandas as pd

DB_PATH = os.path.join("data", "stock_data.db")

class DBManager:
    def __init__(self):
        self._ensure_data_dir()
        self._init_db()

    def _ensure_data_dir(self):
        if not os.path.exists("data"):
            os.makedirs("data")

    def _get_conn(self):
        return sqlite3.connect(DB_PATH)

    def _init_db(self):
        """Initialize database tables if they don't exist."""
        with self._get_conn() as conn:
            c = conn.cursor()
            
            # Table: stocks
            c.execute('''
                CREATE TABLE IF NOT EXISTS stocks (
                    code TEXT PRIMARY KEY,
                    name TEXT,
                    enabled BOOLEAN,
                    memo TEXT
                )
            ''')
            
            # Table: strategy_params
            c.execute('''
                CREATE TABLE IF NOT EXISTS strategy_params (
                    param_key TEXT PRIMARY KEY,
                    param_value TEXT,
                    description TEXT
                )
            ''')
            
            # Table: analysis_results
            c.execute('''
                CREATE TABLE IF NOT EXISTS analysis_results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT,
                    stock_code TEXT,
                    signal TEXT,
                    price REAL,
                    indicators TEXT,
                    created_at TEXT
                )
            ''')

            # --- New Tables for Dual Account System ---
            # Table: accounts
            c.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT, -- 'VIRTUAL' or 'REAL'
                    name TEXT,
                    balance REAL,
                    currency TEXT DEFAULT 'TWD',
                    created_at TEXT
                )
            ''')

            # Table: transactions (Virtual Trading Records)
            c.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER,
                    stock_code TEXT,
                    action TEXT, -- 'BUY' or 'SELL'
                    price REAL,
                    quantity INTEGER,
                    fee REAL,
                    tax REAL,
                    total_amount REAL, -- Net amount (Cost for BUY, Proceeds for SELL)
                    date TEXT,
                    memo TEXT,
                    created_at TEXT,
                    FOREIGN KEY(account_id) REFERENCES accounts(id)
                )
            ''')

            # Table: positions (Virtual Holdings)
            c.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    account_id INTEGER,
                    stock_code TEXT,
                    quantity INTEGER,
                    avg_cost REAL,
                    PRIMARY KEY (account_id, stock_code),
                    FOREIGN KEY(account_id) REFERENCES accounts(id)
                )
            ''')
            
            # Ensure default virtual account exists
            self._ensure_default_account(c)
            # Ensure default real account exists
            self._ensure_real_account(c)

            conn.commit()
        print(f"✅ SQLite Database initialized at {DB_PATH}")

    def _ensure_default_account(self, cursor):
        """Creates a default virtual account if none exists."""
        cursor.execute("SELECT COUNT(*) FROM accounts WHERE type='VIRTUAL'")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute('''
                INSERT INTO accounts (type, name, balance, created_at)
                VALUES (?, ?, ?, ?)
            ''', ('VIRTUAL', '預設模擬帳戶', 100000, datetime.now().isoformat()))
            print("✨ Created default Virtual Account with 100,000 TWD")

    def _ensure_real_account(self, cursor):
        """Creates a default real account if none exists."""
        cursor.execute("SELECT COUNT(*) FROM accounts WHERE type='REAL'")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute('''
                INSERT INTO accounts (type, name, balance, created_at)
                VALUES (?, ?, ?, ?)
            ''', ('REAL', '正式帳戶 (Shioaji)', 0, datetime.now().isoformat()))
            print("✨ Created default Real Account")

    # --- Stocks ---
    def fetch_stock_list(self) -> list:
        """Fetches enabled stocks code list."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT code FROM stocks WHERE enabled = 1")
            rows = c.fetchall()
            return [row[0] for row in rows]

    def fetch_all_stocks(self) -> list:
        """Fetches all stocks for settings."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT code, name, enabled, memo FROM stocks ORDER BY code")
            rows = c.fetchall()
            result = []
            for r in rows:
                result.append({
                    "Stock": r[0],
                    "Name": r[1],
                    "Enabled": bool(r[2]),
                    "Memo": r[3] or ""
                })
            return result

    def save_stock_list(self, stock_list: list) -> bool:
        """Upsert stock list."""
        try:
            with self._get_conn() as conn:
                c = conn.cursor()
                for item in stock_list:
                    code = item.get('Stock')
                    name = item.get('Name')
                    enabled = 1 if (str(item.get('Enabled')).upper() == 'TRUE' or item.get('Enabled') is True) else 0
                    memo = item.get('Memo', '')
                    
                    c.execute('''
                        INSERT INTO stocks (code, name, enabled, memo)
                        VALUES (?, ?, ?, ?)
                        ON CONFLICT(code) DO UPDATE SET
                        name=excluded.name,
                        enabled=excluded.enabled,
                        memo=excluded.memo
                    ''', (code, name, enabled, memo))
                conn.commit()
            print(f"✅ Saved {len(stock_list)} stocks to SQLite.")
            return True
        except Exception as e:
            print(f"❌ Failed to save stocks: {e}")
            return False

    # --- Strategy Config ---
    def fetch_strategy_config(self) -> dict:
        """Returns simple dict {key: value} for backend use."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT param_key, param_value FROM strategy_params")
            rows = c.fetchall()
            config = {}
            for k, v in rows:
                # Try convert to number if possible
                try:
                    if '.' in v:
                        config[k] = float(v)
                    else:
                        config[k] = int(v)
                except:
                    config[k] = v
            return config

    def fetch_strategy_config_full(self) -> list:
        """Returns list of dicts for frontend settings."""
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT param_key, param_value, description FROM strategy_params ORDER BY param_key")
            rows = c.fetchall()
            result = []
            for r in rows:
                # Try convert value
                val = r[1]
                try:
                    if '.' in val:
                        val = float(val)
                    else:
                        val = int(val)
                except:
                    pass
                
                result.append({
                    "Parameter": r[0],
                    "Value": val,
                    "Description": r[2] or ""
                })
            return result

    def save_strategy_config(self, config_dict: dict) -> bool:
        try:
            with self._get_conn() as conn:
                c = conn.cursor()
                for k, v in config_dict.items():
                    val_str = str(v)
                    # Upsert (preserve description if exists, unfortunately SQLite UPSERT with partial update is tricky if we don't have description in input)
                    # Simple approach: Check if exists, update value only
                    c.execute("SELECT 1 FROM strategy_params WHERE param_key = ?", (k,))
                    exists = c.fetchone()
                    
                    if exists:
                        c.execute("UPDATE strategy_params SET param_value = ? WHERE param_key = ?", (val_str, k))
                    else:
                        c.execute("INSERT INTO strategy_params (param_key, param_value, description) VALUES (?, ?, ?)", (k, val_str, ""))
                conn.commit()
            print("✅ Saved strategy config to SQLite.")
            return True
        except Exception as e:
            print(f"❌ Failed to save strategy: {e}")
            return False

    # --- Analysis Results ---
    def save_analysis_result(self, df: pd.DataFrame):
        try:
            with self._get_conn() as conn:
                c = conn.cursor()
                now = datetime.now().isoformat()
                
                for _, row in df.iterrows():
                    date_val = str(row.get('Date'))
                    stock_code = str(row.get('Stock'))
                    signal = row.get('Signal', 'HOLD')
                    try:
                        price = float(str(row.get('Close', 0)).replace(',',''))
                    except:
                        price = 0.0
                    
                    indicators = json.dumps(row.to_dict(), default=str, ensure_ascii=False)
                    
                    c.execute('''
                        INSERT INTO analysis_results (date, stock_code, signal, price, indicators, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (date_val, stock_code, signal, price, indicators, now))
                conn.commit()
            print(f"✅ Saved {len(df)} analysis results to SQLite.")
        except Exception as e:
            print(f"❌ Failed to save analysis results: {e}")

    def fetch_latest_analysis(self):
        """
        Fetches the latest analysis result for each stock.
        Returns list of dicts.
        """
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            # SQLite doesn't have DISTINCT ON. 
            # We can use a subquery/window function or just fetch all sorted and filter in python if simplified.
            # Using Window Function (SQLite 3.25+):
            query = '''
                SELECT ar.*, s.name, s.memo 
                FROM (
                    SELECT *, ROW_NUMBER() OVER (PARTITION BY stock_code ORDER BY date DESC) as rn
                    FROM analysis_results
                ) ar
                LEFT JOIN stocks s ON ar.stock_code = s.code
                WHERE ar.rn = 1
            '''
            try:
                c.execute(query)
            except sqlite3.OperationalError:
                # Fallback
                c.execute("SELECT * FROM analysis_results ORDER BY date DESC")
            
            rows = c.fetchall()
            results = []
            for row in rows:
                # Parse indicators
                indicators = {}
                try:
                    if row['indicators']:
                        indicators = json.loads(row['indicators'])
                except:
                    pass
                
                # Map to Frontend expected format (Title Case)
                row_dict = dict(row)
                res = {
                    "Stock": row_dict.get('stock_code'),
                    "Name": row_dict.get('name', '') or "",
                    "Date": row_dict.get('date'),
                    "Signal": row_dict.get('signal'),
                    "Close": row_dict.get('price'),
                    "Memo": row_dict.get('memo', '') or "",
                    "K": indicators.get('K', 0),
                    "D": indicators.get('D', 0),
                    "RSI": indicators.get('RSI', 0)
                }
                
                # Merge other indicator fields if needed
                # res.update(indicators) 
                
                results.append(res)
            return results

    # --- Account Management Methods ---

    def get_accounts(self):
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM accounts")
            return [dict(row) for row in c.fetchall()]

    def get_account_balance(self, account_id):
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
            res = c.fetchone()
            return res[0] if res else 0.0

    def update_account_balance(self, account_id, amount_change):
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount_change, account_id))
            conn.commit()

    def get_position(self, account_id, stock_code):
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM positions WHERE account_id = ? AND stock_code = ?", (account_id, stock_code))
            row = c.fetchone()
            return dict(row) if row else None

    def get_all_positions(self, account_id):
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM positions WHERE account_id = ?", (account_id,))
            return [dict(row) for row in c.fetchall()]

    def update_position(self, account_id, stock_code, qty_change, price, action):
        """
        Updates position quantity and average cost.
        Simple Average Cost Logic:
        - Buy: Update Avg Cost.
        - Sell: Avg Cost unchanged, realized P&L is calculated at transaction time (this method just updates qty).
        """
        with self._get_conn() as conn:
            c = conn.cursor()
            # Get current
            c.execute("SELECT quantity, avg_cost FROM positions WHERE account_id = ? AND stock_code = ?", (account_id, stock_code))
            row = c.fetchone()
            
            if row:
                current_qty, current_avg = row
                new_qty = current_qty + qty_change
                
                if new_qty == 0:
                    c.execute("DELETE FROM positions WHERE account_id = ? AND stock_code = ?", (account_id, stock_code))
                else:
                    new_avg = current_avg
                    if action == 'BUY':
                        # Weighted Average
                        total_cost = (current_qty * current_avg) + (qty_change * price)
                        new_avg = total_cost / new_qty
                    
                    c.execute("UPDATE positions SET quantity = ?, avg_cost = ? WHERE account_id = ? AND stock_code = ?", 
                              (new_qty, new_avg, account_id, stock_code))
            else:
                # New Position
                if qty_change > 0:
                    c.execute("INSERT INTO positions (account_id, stock_code, quantity, avg_cost) VALUES (?, ?, ?, ?)",
                              (account_id, stock_code, qty_change, price))
            conn.commit()

    def log_transaction(self, account_id, stock_code, action, price, qty, fee, tax, total_amount, memo=""):
        with self._get_conn() as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO transactions (account_id, stock_code, action, price, quantity, fee, tax, total_amount, date, memo, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (account_id, stock_code, action, price, qty, fee, tax, total_amount, datetime.now().isoformat(), memo, datetime.now().isoformat()))
            conn.commit()

    def get_transactions(self, account_id):
        with self._get_conn() as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM transactions WHERE account_id = ? ORDER BY date DESC", (account_id,))
            return [dict(row) for row in c.fetchall()]

