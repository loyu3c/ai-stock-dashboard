import pandas as pd
import time
from data_fetcher import DataFetcher
from strategy_analyzer import StrategyAnalyzer

class MarketScanner:
    def __init__(self, stock_list: list = None):
        if stock_list is None:
            # Default list (Top weighted stocks in TWSE)
            self.stock_list = ["2330", "2317", "2454", "2308", "2303"] 
        else:
            self.stock_list = stock_list
            
        self.fetcher = DataFetcher()

    def run_scan(self) -> pd.DataFrame:
        """
        Iterates over the stock list, fetches data, runs analysis,
        and returns a summary DataFrame of today's signals.
        """
        results = []
        print(f"🚀 Starting Market Scan for {len(self.stock_list)} stocks...")

        for code in self.stock_list:
            # 1. Fetch Data
            df = self.fetcher.fetch_daily_k(code)
            
            if df is None or df.empty:
                print(f"⚠️ No data for {code}")
                continue
                
            # 2. Analyze Strategy
            df = StrategyAnalyzer.analyze(df)
            
            # 3. Get Latest Signal (Today)
            latest = df.iloc[-1]
            
            results.append({
                "Stock": code,
                "Date": latest.name.strftime("%Y-%m-%d"),
                "Close": latest['Close'],
                "Signal": latest['Signal'],
                "Memo": latest['Signal_Memo'],
                "K": round(latest['K'], 2),
                "D": round(latest['D'], 2),
                "RSI": round(latest['RSI'], 2)
            })
            
            # Rate limit prevents API throttling
            time.sleep(1)

        # 4. Create Summary DataFrame
        summary_df = pd.DataFrame(results)
        
        # Sort by Signal (Green first for excitement!)
        if not summary_df.empty:
            summary_df.sort_values(by="Signal", ascending=True, inplace=True) # Green < Red < Yellow (Unicode sort order might vary, usually safe enough)
        
        return summary_df

if __name__ == "__main__":
    # Test Run
    scanner = MarketScanner() # Default list
    report = scanner.run_scan()
    
    print("\n--- Daily Market Report ---")
    print(report.to_markdown(index=False))
    
    # Save to CSV
    report.to_csv("daily_report.csv", index=False, encoding='utf-8-sig')
    print("\n✅ Report saved to daily_report.csv")
