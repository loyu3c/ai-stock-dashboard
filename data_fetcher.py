import pandas as pd
import os
from datetime import datetime, timedelta
from shioaji_login import ShioajiLogin

class DataFetcher:
    def __init__(self):
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _get_api(self):
        return ShioajiLogin.get_api()

    @property
    def api(self):
        return self._get_api()

    def fetch_daily_k(self, stock_code: str, start_date: str = None, end_date: str = None):
        """
        Fetch daily K-lines for a given stock code.
        Default fetches last 365 days.
        Checks local cache first.
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        # 1. Check Cache
        filename = os.path.join(self.data_dir, f"{stock_code}.csv")
        try:
            if os.path.exists(filename):
                # Check modification time
                mod_time = datetime.fromtimestamp(os.path.getmtime(filename))
                # If modified today (or close enough? simple rule: today), use cache.
                # Actually, simplified rule: if file exists, read it. 
                # Optimization relies on data being present. 
                # If user wants FRESH data, they can delete cache or we add force_refresh flag.
                # Let's enforce "modified today" to ensure data is not stale.
                is_today = mod_time.date() == datetime.now().date()
                
                # However, for backtesting past history, old data is fine too if it covers the range.
                # But to be safe and simple: "If file exists and modified today, use it."
                if is_today:
                    print(f"📦 Loading {stock_code} from cache ({filename})...")
                    df_daily = pd.read_csv(filename, index_col='Date', parse_dates=True)
                    # Filter date range if needed? Usually backtest engine handles slicing.
                    return df_daily
        except Exception as e:
             print(f"⚠️ Cache read error: {e}")

        # 2. Fetch from API
        print(f"📥 Fetching {stock_code} from {start_date} to {end_date} (API)...")
        
        try:
            api = self._get_api()
            contract = api.Contracts.Stocks[stock_code]
            kbars = api.kbars(
                contract=contract, 
                start=start_date, 
                end=end_date
            )
            
            df = pd.DataFrame({**kbars})
            df.ts = pd.to_datetime(df.ts)
            df.set_index('ts', inplace=True)
            df.index.name = 'Date'
            
            # Resample to Daily
            # Open=first, High=max, Low=min, Close=last, Volume=sum
            df_daily = df.resample('D').agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            })
            # Remove empty days (non-trading days)
            df_daily.dropna(inplace=True)
            
            # Save to CSV
            df_daily.to_csv(filename)
            print(f"✅ Saved {len(df_daily)} rows (Daily K) to {filename}")
            
            return df_daily
            
            
        except Exception as e:
            print(f"❌ Failed to fetch {stock_code}: {e}")
            return None

    def get_stock_name(self, stock_code: str) -> str:
        """
        Get stock name from contract.
        """
        try:
            contract = self._get_api().Contracts.Stocks[stock_code]
            return contract.name
        except Exception:
            return stock_code # Fallback to code if name not found

if __name__ == "__main__":
    # Test run
    fetcher = DataFetcher()
    fetcher.fetch_daily_k("2330") # TSMC
