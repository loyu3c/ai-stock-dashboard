import pandas as pd
import pandas_ta as ta

class TechIndicators:
    @staticmethod
    def calculate(df: pd.DataFrame, 
                  ma_short: int = 10, ma_long: int = 20, 
                  rsi_len: int = 14, 
                  kd_k: int = 9, kd_d: int = 3,
                  macd_fast: int = 12, macd_slow: int = 26, macd_signal: int = 9) -> pd.DataFrame:
        """
        Calculates technical indicators: MA, MACD, RSI, KD.
        Appends columns to the input DataFrame.
        """
        if df.empty:
            return df
        
        # Ensure 'Close' is present
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")

        # 1. Moving Averages
        df['MA_SHORT'] = ta.sma(df['Close'], length=ma_short) 
        df['MA_LONG'] = ta.sma(df['Close'], length=ma_long)  
        df['MA60'] = ta.sma(df['Close'], length=60) 

        # 2. MACD
        macd = ta.macd(df['Close'], fast=macd_fast, slow=macd_slow, signal=macd_signal)
        if macd is not None:
            # pandas_ta columns: MACD_{fast}_{slow}_{signal}
            # We need to construct dynamic column names
            col_main = f'MACD_{macd_fast}_{macd_slow}_{macd_signal}'
            col_signal = f'MACDs_{macd_fast}_{macd_slow}_{macd_signal}'
            col_hist = f'MACDh_{macd_fast}_{macd_slow}_{macd_signal}'

            # Check if columns exist (pandas_ta creates them)
            if col_main in macd.columns:
                df['MACD_DIF'] = macd[col_main]
                df['MACD_DEM'] = macd[col_signal]
                df['MACD_OSC'] = macd[col_hist]

        # 3. RSI
        df['RSI'] = ta.rsi(df['Close'], length=rsi_len)

        # 4. KD (Stochastic Oscillator)
        stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=kd_k, d=kd_d)
        if stoch is not None:
             # pandas_ta columns: STOCHk_{k}_{d}_{3}, STOCHd_{k}_{d}_{3} (Wait, stoch default smooth_k=3)
             # Let's handle the default column naming or use iloc if needed, but names are safer.
             # Default STOCH function in pandas_ta: k=14, d=3, smooth_k=3. 
             # We passed k=kd_k, d=kd_d. 
             # Assumption: smooth_k is 3 by default in pandas_ta stoch unless specified.
             # Let's check keys if needed, but for now we try to construct them.
             # Actually, simpler is to just take the first and second columns if we are sure.
             df['K'] = stoch.iloc[:, 0]
             df['D'] = stoch.iloc[:, 1]

        return df

if __name__ == "__main__":
    # Simple test
    import os
    file_path = "data/2330.csv"
    if os.path.exists(file_path):
        df = pd.read_csv(file_path, index_col=0, parse_dates=True)
        print("Original columns:", df.columns.tolist())
        
        df = TechIndicators.calculate(df)
        print("Calculated columns:", df.columns.tolist())
        
        # Check last row
        print("\nLast Row Data:")
        print(df.iloc[-1][['Close', 'MA10', 'MA20', 'RSI', 'K', 'D', 'MACD_OSC']])
    else:
        print("Test file not found. Please run data_fetcher.py first.")
