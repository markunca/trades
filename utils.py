# utils.py
import ccxt
import pandas as pd

def fetch_data(symbol, timeframe, since, limit=30):
    binance = ccxt.binance()
    data = binance.fetch_ohlcv(symbol, timeframe, since=since, limit=limit)
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df