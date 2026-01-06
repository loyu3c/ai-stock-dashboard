import pandas as pd
import time
from data_fetcher import DataFetcher
from strategy_analyzer import StrategyAnalyzer

class MarketScanner:
    def __init__(self, stock_list: list = None, config: dict = {}):
        if stock_list is None:
            # Default list (Top weighted stocks in TWSE)
            self.stock_list = ["2330", "2317", "2454", "2308", "2303"] 
        else:
            self.stock_list = stock_list
            
        self.config = config
        self.fetcher = DataFetcher()

    def get_market_candidates(self, scan_type: str = 'volume_rank', limit: int = 10) -> list:
        """
        Scans the market to find potential candidates.
        """
        api = self.fetcher.api
        candidates = []
        
        print(f"🔍 Scanning market for {scan_type} (Limit: {limit})...")
        
        # 1. Filter Common Stocks (TSE & OTC)
        # Using a list comprehension is fast
        try:
            # TSE
            if hasattr(api.Contracts.Stocks, 'TSE'):
                candidates.extend([c for c in api.Contracts.Stocks.TSE if c.security_type == 'STK' and len(c.code) == 4])
            # OTC
            if hasattr(api.Contracts.Stocks, 'OTC'):
                candidates.extend([c for c in api.Contracts.Stocks.OTC if c.security_type == 'STK' and len(c.code) == 4])
                
        except Exception as e:
            print(f"❌ Error getting contracts: {e}")
            return []
            
        # 2. Snapshot Data
        snapshots = []
        batch_size = 500
        for i in range(0, len(candidates), batch_size):
            batch = candidates[i:i+batch_size]
            try:
                snaps = api.snapshots(batch)
                snapshots.extend(snaps)
            except Exception as e:
                print(f"⚠️ Snapshot batch failed: {e}")
        
        # 3. Sort by Criteria
        if scan_type == 'volume_rank':
            # Sort by total_volume descending
            snapshots.sort(key=lambda s: s.total_volume, reverse=True)
            
        # 4. Return Top N Codes
        top_n = snapshots[:limit]
        return [s.code for s in top_n]

    def _load_opt_results(self):
        """Loads optimization results from JSON."""
        import json
        import os
        path = "data/optimization_results.json"
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def run_scan(self, target_list: list = None) -> pd.DataFrame:
        """
        Iterates over the stock list, fetches data, runs analysis,
        and returns a summary DataFrame of today's signals.
        """
        # Load Optimized Params
        opt_results = self._load_opt_results()
        
        # Use provided list or default
        scan_list = target_list if target_list is not None else self.stock_list
        
        results = []
        print(f"🚀 Starting Market Scan for {len(scan_list)} stocks...")

        for code in scan_list:
            # 1. Fetch Data
            df = self.fetcher.fetch_daily_k(code)
            stock_name = self.fetcher.get_stock_name(code)
            
            if df is None or df.empty:
                print(f"⚠️ No data for {code}")
                continue
                
            # 2. Determine Config (Hybrid Strategy)
            # Default to global config
            current_config = self.config.copy()
            
            # If optimized params exist, override
            if code in opt_results:
                best = opt_results[code].get('best', {})
                params = best.get('params', {})
                if params:
                    # Map optimization param names to StrategyAnalyzer config keys if needed
                    # Currently StrategyAnalyzer expects: MA_SHORT_DAYS, RSI_THRESHOLD, etc.
                    # Optimization outputs: ma_short, rsi_threshold (usually lowercase from optimizer.py)
                    # We need to ensure keys match. Let's assume optimizer saves compatible keys or we map them.
                    # Checking optimizer.py would be safer, but let's try direct update and mapping.
                    
                    # Map known keys just in case
                    if 'ma_short' in params: current_config['MA_SHORT_DAYS'] = params['ma_short']
                    if 'ma_long' in params: current_config['MA_LONG_DAYS'] = params['ma_long']
                    if 'rsi_threshold' in params: current_config['RSI_THRESHOLD'] = params['rsi_threshold']
                    if 'kd_threshold' in params: current_config['KD_THRESHOLD'] = params['kd_threshold']
                    
                    # Also try direct update for exact matches
                    current_config.update(params)
                    # print(f"🎯 Applied optimized params for {code}")

            # 3. Analyze Strategy
            df = StrategyAnalyzer.analyze(df, config=current_config)
            
            # 4. Get Latest Signal (Today)
            latest = df.iloc[-1]
            try:
                # Handle potential missing columns if analysis failed
                signal = latest.get('Signal', '⚪')
                
                results.append({
                    "Stock": code,
                    "Name": stock_name,
                    "Date": latest.name.strftime("%Y-%m-%d"),
                    "Close": latest['Close'],
                    "Signal": signal,
                    "Memo": latest.get('Signal_Memo', ''),
                    "K": round(latest.get('K', 0), 2),
                    "D": round(latest.get('D', 0), 2),
                    "RSI": round(latest.get('RSI', 0), 2),
                    "Volume": int(latest.get('Volume', 0))
                })
            except Exception as e:
                print(f"❌ Error processing result for {code}: {e}")
            
            # Rate limit prevents API throttling (reduce for scanner to be faster?)
            # For 20 stocks, 1s sleep = 20s. 0.5s = 10s.
            time.sleep(0.1) # Speed up slightly

        # 5. Create Summary DataFrame
        summary_df = pd.DataFrame(results)
        
        # Sort by Signal (Green first for excitement!)
        if not summary_df.empty:
            summary_df.sort_values(by="Signal", ascending=True, inplace=True) 
        
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
