import pandas as pd
import os
from datetime import datetime, timedelta
from shioaji_login import ShioajiLogin

class DataFetcher:
    def __init__(self):
        self.api = ShioajiLogin.get_api()
        self.data_dir = "data"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch_daily_k(self, stock_code: str, start_date: str = None, end_date: str = None):
        """
        Fetch daily K-lines for a given stock code.
        Default fetches last 365 days.
        """
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")

        print(f"📥 Fetching {stock_code} from {start_date} to {end_date}...")
        
        try:
            contract = self.api.Contracts.Stocks[stock_code]
            kbars = self.api.kbars(
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
            filename = os.path.join(self.data_dir, f"{stock_code}.csv")
            df_daily.to_csv(filename)
            print(f"✅ Saved {len(df_daily)} rows (Daily K) to {filename}")
            
            return df_daily
            
        except Exception as e:
            print(f"❌ Failed to fetch {stock_code}: {e}")
            return None

if __name__ == "__main__":
    # Test run
    fetcher = DataFetcher()
    fetcher.fetch_daily_k("2330") # TSMC
