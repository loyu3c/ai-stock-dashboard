import pandas as pd
import pandas_ta as ta

class TechIndicators:
    @staticmethod
    def calculate(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates technical indicators: MA, MACD, RSI, KD.
        Appends columns to the input DataFrame.
        """
        if df.empty:
            return df
        
        # Ensure 'Close' is present
        if 'Close' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' column")

        # 1. Moving Averages (SMA 10, 20)
        df['MA10'] = ta.sma(df['Close'], length=10)
        df['MA20'] = ta.sma(df['Close'], length=20)
        df['MA60'] = ta.sma(df['Close'], length=60) # Added MA60 for reference

        # 2. MACD (Fast=12, Slow=26, Signal=9)
        macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
        if macd is not None:
            # pandas_ta returns columns like MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
            # We standardize them for easier access
            df['MACD_DIF'] = macd['MACD_12_26_9']  # Fast - Slow
            df['MACD_DEM'] = macd['MACDs_12_26_9'] # Signal line
            df['MACD_OSC'] = macd['MACDh_12_26_9'] # Histogram

        # 3. RSI (14)
        df['RSI'] = ta.rsi(df['Close'], length=14)

        # 4. KD (Stochastic Oscillator)
        # pandas_ta uses stoch(high, low, close) -> STOCHk, STOCHd
        stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=9, d=3)
        if stoch is not None:
            df['K'] = stoch['STOCHk_9_3_3']
            df['D'] = stoch['STOCHd_9_3_3']

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
