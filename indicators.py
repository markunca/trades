# indicators.py
import pandas as pd
from ta.momentum import RSIIndicator, StochRSIIndicator

def calculate_indicators(df):
    df['RSI'] = RSIIndicator(df['close']).rsi()
    stoch_rsi_indicator = StochRSIIndicator(df['close'])
    df['stoch_rsi'] = stoch_rsi_indicator.stochrsi()
    df['daily_avg'] = df['close'].rolling(window=LOOKBACK_PERIOD).mean()
    return df