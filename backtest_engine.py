import pandas as pd
from strategy_analyzer import StrategyAnalyzer
from data_fetcher import DataFetcher

class BacktestEngine:
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.fetcher = DataFetcher()

    def run(self, stock_code: str, start_date: str, end_date: str, strategy_config: dict = {}) -> dict:
        """
        Runs a backtest for the given stock and date range.
        """
        # 1. Fetch Data
        df = self.fetcher.fetch_daily_k(stock_code, start_date, end_date)
        if df is None or df.empty:
            return {"error": "No data found"}
            
        # 2. Apply Strategy
        df = StrategyAnalyzer.analyze(df, config=strategy_config)
        
        # 3. Simulate Trading
        capital = self.initial_capital
        position = 0 # 0 = flat, 1 = hold
        entry_price = 0
        trades = []
        equity_curve = []
        
        for date, row in df.iterrows():
            signal = row.get('Signal', '🟡')
            price = row['Close']
            
            # --- Buy Logic ---
            if signal == '🟢' and position == 0:
                # Buy Max Shares (Round down to 1000 shares if TW stock? Simplified: Fractional allowed for ROI calc)
                # Let's assume we buy as much as possible
                shares = capital / price
                position = shares
                capital = 0
                entry_price = price
                
                trades.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "type": "BUY",
                    "price": price,
                    "reason": row.get('Signal_Memo', '')
                })
                
            # --- Sell Logic ---
            elif signal == '🔴' and position > 0:
                # Sell All
                proceeds = position * price
                capital = proceeds
                profit = (price - entry_price) * position
                profit_pct = (price - entry_price) / entry_price * 100
                
                position = 0
                entry_price = 0
                
                trades.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "type": "SELL",
                    "price": price,
                    "profit": round(profit, 0),
                    "profit_pct": round(profit_pct, 2),
                    "reason": row.get('Signal_Memo', '')
                })
                
            # Track Equity (Cash + Market Value of Stock)
            current_equity = capital + (position * price)
            equity_curve.append({
                "date": date.strftime("%Y-%m-%d"),
                "equity": round(current_equity, 0),
                "price": price,
                "signal": signal if signal in ['🟢', '🔴'] else None # Only mark buy/sell on chart
            })
            
        # Force sell at end if holding
        if position > 0:
             final_price = df.iloc[-1]['Close']
             proceeds = position * final_price
             capital = proceeds
             trades.append({
                    "date": df.index[-1].strftime("%Y-%m-%d"),
                    "type": "SELL (End)",
                    "price": final_price,
                    "profit": round((final_price - entry_price) * position, 0),
                    "profit_pct": round((final_price - entry_price) / entry_price * 100, 2),
                    "reason": "End of Backtest"
                })

        # 4. Statistics
        total_return_pct = (capital - self.initial_capital) / self.initial_capital * 100
        
        winning_trades = [t for t in trades if t['type'].startswith('SELL') and t['profit'] > 0]
        losing_trades = [t for t in trades if t['type'].startswith('SELL') and t['profit'] <= 0]
        total_closed_trades = len(winning_trades) + len(losing_trades)
        
        win_rate = (len(winning_trades) / total_closed_trades * 100) if total_closed_trades > 0 else 0
        
        return {
            "stock": stock_code,
            "summary": {
                "total_return_pct": round(total_return_pct, 2),
                "start_capital": self.initial_capital,
                "end_capital": round(capital, 0),
                "total_trades": total_closed_trades,
                "win_count": len(winning_trades),
                "loss_count": len(losing_trades),
                "win_rate": round(win_rate, 1)
            },
            "trades": trades,
            "daily_history": equity_curve
        }

if __name__ == "__main__":
    engine = BacktestEngine()
    result = engine.run("2330", "2024-01-01", "2024-12-31")
    print(result['summary'])
    print(f"Trades: {len(result['trades'])}")
