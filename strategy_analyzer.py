import pandas as pd
from tech_indicators import TechIndicators

class StrategyAnalyzer:
    
    @staticmethod
    def analyze(df: pd.DataFrame, config: dict = {}) -> pd.DataFrame:
        """
        Analyzes the DataFrame and determines the signal colors.
        Returns the DataFrame with 'Signal' and 'Signal_Memo' columns.
        """
        # Load Config
        ma_short = int(config.get('MA_SHORT_DAYS', 10))
        ma_long = int(config.get('MA_LONG_DAYS', 20))
        rsi_thresh = int(config.get('RSI_THRESHOLD', 80))
        kd_thresh = int(config.get('KD_THRESHOLD', 50))
        
        macd_fast = int(config.get('MACD_FAST', 12))
        macd_slow = int(config.get('MACD_SLOW', 26))
        macd_signal = int(config.get('MACD_SIGNAL', 9))
        
        # 1. Calculate Indicators
        df = TechIndicators.calculate(df, 
                                      ma_short=ma_short, ma_long=ma_long,
                                      macd_fast=macd_fast, macd_slow=macd_slow, macd_signal=macd_signal)
        
        # 2. Define Signal Columns initialized to 'Yellow'
        df['Signal'] = '🟡'
        df['Signal_Memo'] = 'Hold/Observe'
        
        # 3. Vectorized Conditions
        
        # --- Green Light Conditions (Buy) ---
        # 1. Price > MA_LONG (Trend is up)
        cond_trend_up = df['Close'] > df['MA_LONG']
        
        # 2. MACD Histogram > 0 (Momentum is positive)
        cond_macd_pos = df['MACD_OSC'] > 0
        
        # 3. KD Golden Cross (Low level < Threshold)
        # Current K > D AND Previous K < D
        cond_kd_cross = (df['K'] > df['D']) & (df['K'].shift(1) < df['D'].shift(1))
        cond_kd_low = df['K'] < kd_thresh 
        
        green_mask = cond_trend_up & cond_macd_pos & cond_kd_cross & cond_kd_low
        
        # --- Red Light Conditions (Sell) ---
        # 1. Price < MA_SHORT (Short term weakness)
        cond_trend_weak = df['Close'] < df['MA_SHORT']
        
        # 2. RSI Overbought
        cond_rsi_high = df['RSI'] > rsi_thresh
        
        red_mask = cond_trend_weak | cond_rsi_high
        
        # 4. Apply Signals (Red takes precedence over Green if conflicting, though rare)
        df.loc[green_mask, 'Signal'] = '🟢'
        df.loc[green_mask, 'Signal_Memo'] = f'Buy: Trend Up + KD<{kd_thresh} Gold Cross'
        
        df.loc[red_mask, 'Signal'] = '🔴'
        df.loc[red_mask, 'Signal_Memo'] = f'Sell: Below MA{ma_short} or RSI>{rsi_thresh}'
        
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
