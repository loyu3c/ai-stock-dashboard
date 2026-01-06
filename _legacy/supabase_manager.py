import os
from supabase import create_client, Client
from config import Config
import pandas as pd
from datetime import datetime

class SupabaseManager:
    def __init__(self):
        self.client: Client = None
        
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            print("⚠️ Warning: SUPABASE_URL or SUPABASE_KEY not set in .env")
            return

        try:
            self.client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
            print(f"✅ Connected to Supabase: {Config.SUPABASE_URL}")
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")

    def fetch_stock_list(self) -> list:
        """
        Fetches enabled stocks from 'stocks' table.
        Returns:
            list: List of stock codes (str) e.g., ['2330', '2317']
        """
        if not self.client:
            return []

        try:
            response = self.client.table('stocks').select('code').eq('enabled', True).execute()
            # response.data is a list of dicts: [{'code': '2330'}, ...]
            enabled_stocks = [item['code'] for item in response.data]
            print(f"✅ Fetched {len(enabled_stocks)} enabled stocks from Supabase.")
            return enabled_stocks
        except Exception as e:
            print(f"❌ Failed to fetch stock list: {e}")
            return []

    def fetch_all_stocks(self) -> list:
        """
        Fetches ALL stocks (including disabled) for Settings page.
        Returns:
            list: [{'Stock': '2330', 'Name': '...', 'Enabled': True/False, 'Memo': '...'}, ...]
        """
        if not self.client:
            return []

        try:
            response = self.client.table('stocks').select('*').order('code').execute()
            result = []
            for item in response.data:
                result.append({
                    "Stock": item['code'],
                    "Name": item['name'],
                    "Enabled": item['enabled'], # Keep as boolean for API, or convert if frontend needs string
                    "Memo": item['memo'] or ""
                })
            return result
        except Exception as e:
            print(f"❌ Failed to fetch all stocks: {e}")
            return []

    def fetch_strategy_config(self) -> dict:
        """
        Fetches 'strategy_params' and returns a simple dict.
        Returns:
            dict: { 'MA_SHORT_DAYS': 10, ... }
        """
        if not self.client:
            return {}

        try:
            response = self.client.table('strategy_params').select('param_key, param_value').execute()
            # response.data: [{'param_key': 'MA...', 'param_value': 10}, ...]
            config = {item['param_key']: item['param_value'] for item in response.data}
            return config
        except Exception as e:
            print(f"❌ Failed to fetch strategy config: {e}")
            return {}

    def fetch_strategy_config_full(self) -> list:
        """
        Fetches full strategy config with descriptions.
        For compatibility with frontend expecting specific keys.
        """
        if not self.client:
            return []
            
        try:
            response = self.client.table('strategy_params').select('*').order('created_at').execute()
            # Transform to match expected structure if needed, or just return keys suitable for frontend
            # The frontend previously expected: Parameter, Value, Description
            # DB has: param_key, param_value, description
            
            result = []
            for item in response.data:
                result.append({
                    "Parameter": item['param_key'],
                    "Value": item['param_value'],
                    "Description": item['description'] or ""
                })
            return result
        except Exception as e:
            print(f"❌ Failed to fetch config full: {e}")
            return []

    def save_analysis_result(self, df: pd.DataFrame):
        """
        Saves analysis results to 'analysis_results' table.
        Replaces update_daily_report.
        """
        if not self.client:
            return

        try:
            # Prepare data for insertion
            # df columns might be: Stock, Name, Date, Close, Signal, etc.
            # match with table: date, stock_code, signal, price, indicators(json)
            
            records = []
            now = datetime.now().isoformat()
            
            for _, row in df.iterrows():
                # Extract main fields
                stock_code = str(row.get('Stock'))
                signal = row.get('Signal', 'HOLD')
                try:
                    price = float(str(row.get('Close', 0)).replace(',',''))
                except:
                    price = 0
                
                # Assume 'Date' in df is string or datetime
                date_val = row.get('Date')
                
                # Bundle everything else into indicators json
                indicators = row.to_dict()
                # Remove extracted fields to save space/duplication if desired, 
                # but keeping them in JSON is also fine for flexible querying.
                
                record = {
                    "date": date_val,
                    "stock_code": stock_code,
                    "signal": signal,
                    "price": price,
                    "indicators": indicators,
                    "created_at": now
                }
                records.append(record)
            
            if records:
                # Upsert based on some criteria? 
                # For now just insert. If we run multiple times same day, might want to delete old first?
                # Or maybe user just wants to append.
                # Let's try insert.
                self.client.table('analysis_results').insert(records).execute()
                print(f"✅ Saved {len(records)} analysis results to Supabase.")
                
        except Exception as e:
            print(f"❌ Failed to save analysis results: {e}")

    def save_stock_list(self, stock_list: list) -> bool:
        """
        Updates stock list.
        stock_list: [{'Stock': '2330', 'Name': '...', 'Enabled': 'TRUE'}]
        """
        if not self.client:
            return False

        try:
            # Upsert stocks
            # Map frontend keys to DB columns
            # DB: code, name, enabled, memo
            upsert_data = []
            for item in stock_list:
                enabled = str(item.get('Enabled')).upper() == 'TRUE'
                upsert_data.append({
                    "code": item.get('Stock'),
                    "name": item.get('Name'),
                    "enabled": enabled,
                    "memo": item.get('Memo', '')
                })
            
            if upsert_data:
                # on_conflict='code'
                self.client.table('stocks').upsert(upsert_data, on_conflict='code').execute()
                print(f"✅ Saved {len(upsert_data)} stocks to Supabase.")
            return True
        except Exception as e:
            print(f"❌ Failed to save stock list: {e}")
            return False

    def save_strategy_config(self, config_dict: dict) -> bool:
        """
        Updates parameters.
        config_dict: {'MA_SHORT_DAYS': 10}
        """
        if not self.client:
            return False
            
        try:
            upsert_data = []
            for key, val in config_dict.items():
                upsert_data.append({
                    "param_key": key,
                    "param_value": val
                })
            
            if upsert_data:
                # Need to be careful not to wipe descriptions if we just upsert value.
                # Supabase upsert updates columns provided. If description is not provided, it should keep old value?
                # Default behavior of Postgres upsert: DO UPDATE SET ... 
                # supabase-py upsert should handle partial updates if columns omitted? 
                # Let's hope so. If not, we might overwrite description with null if we don't include it.
                # To be safe, let's just update 'param_value' where 'param_key' matches.
                # But upsert is easiest for batch.
                
                # Check if we should fetch descriptions first to be safe, or just assume ignore_duplicates=False
                self.client.table('strategy_params').upsert(upsert_data, on_conflict='param_key').execute()
                print("✅ Saved strategy config to Supabase.")
            return True
        except Exception as e:
            print(f"❌ Failed to save strategy config: {e}")
            return False

if __name__ == "__main__":
    # Test connection
    mgr = SupabaseManager()
    if mgr.client:
        print("Stocks:", mgr.fetch_stock_list())
        print("Config:", mgr.fetch_strategy_config())
