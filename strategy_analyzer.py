import pandas as pd
from tech_indicators import TechIndicators

class StrategyAnalyzer:
    
    @staticmethod
    def analyze(df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyzes the DataFrame and determines the signal colors.
        Returns the DataFrame with 'Signal' and 'Signal_Memo' columns.
        """
        # 1. Calculate Indicators
        df = TechIndicators.calculate(df)
        
        # 2. Define Signal Columns initialized to 'Yellow'
        df['Signal'] = '🟡'
        df['Signal_Memo'] = 'Hold/Observe'
        
        # 3. Vectorized Conditions
        
        # --- Green Light Conditions (Buy) ---
        # 1. Price > MA20 (Trend is up)
        cond_trend_up = df['Close'] > df['MA20']
        
        # 2. MACD Histogram > 0 (Momentum is positive)
        cond_macd_pos = df['MACD_OSC'] > 0
        
        # 3. KD Golden Cross (Low level < 50 for better sensitivity, or 30 for strict)
        # Current K > D AND Previous K < D
        cond_kd_cross = (df['K'] > df['D']) & (df['K'].shift(1) < df['D'].shift(1))
        cond_kd_low = df['K'] < 50  # relaxed from 30 to get more signals in testing
        
        green_mask = cond_trend_up & cond_macd_pos & cond_kd_cross & cond_kd_low
        
        # --- Red Light Conditions (Sell) ---
        # 1. Price < MA10 (Short term weakness)
        cond_trend_weak = df['Close'] < df['MA10']
        
        # 2. RSI Overbought
        cond_rsi_high = df['RSI'] > 80
        
        red_mask = cond_trend_weak | cond_rsi_high
        
        # 4. Apply Signals (Red takes precedence over Green if conflicting, though rare)
        df.loc[green_mask, 'Signal'] = '🟢'
        df.loc[green_mask, 'Signal_Memo'] = 'Buy: Trend Up + KD Low Gold Cross'
        
        df.loc[red_mask, 'Signal'] = '🔴'
        df.loc[red_mask, 'Signal_Memo'] = 'Sell: Below MA10 or RSI Overbought'
        
        return df

if __name__ == "__main__":
    import os
    file_path = "data/2330.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, index_col=0, parse_dates=True)
        df = StrategyAnalyzer.analyze(df)
        
        # Show last 10 days
        print(df[['Close', 'MA10', 'MA20', 'K', 'D', 'Signal', 'Signal_Memo']].tail(10))
        
        # Show any Green lights in history
        print("\n--- Recent Green Signals ---")
        print(df[df['Signal'] == '🟢'][['Close', 'Signal_Memo']].tail(5))
    else:
        print("Data file not found.")
