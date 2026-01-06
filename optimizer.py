from itertools import product
from backtest_engine import BacktestEngine
from data_fetcher import DataFetcher
import pandas as pd

class StrategyOptimizer:
    def __init__(self):
        # Define Hyperparameter Space
        self.param_grid = {
            'MA_SHORT_DAYS': [5, 10, 20],
            'MA_LONG_DAYS': [20, 40, 60],
            'RSI_THRESHOLD': [70, 75, 80],
            'KD_THRESHOLD': [50, 80]
        }

    def optimize_stream(self, stock_code: str, start_date: str, end_date: str):
        """
        Generator that yields progress updates and final result.
        """
        yield {"status": "starting", "msg": f"Starting optimization for {stock_code}...", "stock": stock_code}
        
        keys = list(self.param_grid.keys())
        values = list(self.param_grid.values())
        combinations = list(product(*values))
        
        results = []
        engine = BacktestEngine(initial_capital=100000)
        
        total_combs = len(combinations)
        
        for i, comb in enumerate(combinations):
            params = dict(zip(keys, comb))
            
            if params['MA_SHORT_DAYS'] >= params['MA_LONG_DAYS']:
                continue
            
            # Simulate slight delay so user can see progress (optional, but helpful for UX if calc is too fast)
            # import time; time.sleep(0.01)
            
            msg = f"Testing [{i+1}/{total_combs}] MA {params['MA_SHORT_DAYS']}/{params['MA_LONG_DAYS']}..."
            yield {"status": "running", "msg": msg, "progress": round((i+1)/total_combs*100, 0)}
            
            res = engine.run(stock_code, start_date, end_date, strategy_config=params)
            
            if "error" not in res:
                roi = res['summary']['total_return_pct']
                trades = res['summary']['total_trades']
                win_rate = res['summary']['win_rate']
                
                results.append({
                    "params": params,
                    "roi": roi,
                    "win_rate": win_rate,
                    "trades": trades
                })
        
        if results:
            results.sort(key=lambda x: x['roi'], reverse=True)
            best = results[0]
            yield {"status": "done", "msg": "Optimization Complete.", "result": {
                "best": best,
                "top_5": results[:5],
                "total_tested": len(results)
            }}
        else:
            yield {"status": "done", "msg": "No valid results found.", "result": None}

    def optimize(self, stock_code: str, start_date: str, end_date: str):
        # Sync version (Backwards compatibility)
        gen = self.optimize_stream(stock_code, start_date, end_date)
        last_val = None
        for val in gen:
            last_val = val
        
        if last_val and 'result' in last_val:
            return last_val['result']
        return {}

if __name__ == "__main__":
    opt = StrategyOptimizer()
    res = opt.optimize("2330", "2024-01-01", "2024-12-31")
    for r in res['top_5']:
        print(f"ROI: {r['roi']}% | Params: {r['params']}")
