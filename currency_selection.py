# currency_selection.py

import ccxt
import numpy as np

def fetch_data(exchange, symbol, timeframe='1h', limit=100):
    """Fetch historical OHLCV data for a symbol."""
    bars = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    return np.array(bars)

def calculate_sma(data, window):
    """Calculate Simple Moving Average."""
    return np.convolve(data, np.ones(window), 'valid') / window

def calculate_rsi(data, periods=14):
    """Calculate Relative Strength Index."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=periods, min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=periods, min_periods=1).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_currency(exchange, symbol):
    """Analyze a currency to decide if it's a good candidate for trading."""
    data = fetch_data(exchange, symbol)
    if data.size < 1:
        return False  # Not enough data

    close_prices = data[:, 4]  # Use closing prices
    sma_short = calculate_sma(close_prices, window=7)[-1]
    sma_long = calculate_sma(close_prices, window=25)[-1]
    rsi = calculate_rsi(close_prices)[-1]

    # Example criteria: short SMA above long SMA and RSI not in overbought territory
    if sma_short > sma_long and rsi < 70:
        return True
    return False

def select_currency(exchange, symbols):
    """Select the best currency to trade."""
    for symbol in symbols:
        if analyze_currency(exchange, symbol):
            return symbol
    return None

def get_top_currencies(exchange, base_currency='USDT', limit=30):
    """Get top traded currencies based on volume."""
    markets = exchange.load_markets()
    symbols = [market for market in markets if market.endswith(f'/{base_currency}') and market in exchange.symbols]
    volumes = {symbol: exchange.fetch_ticker(symbol)['quoteVolume'] for symbol in symbols}
    sorted_symbols = sorted(volumes, key=volumes.get, reverse=True)
    return sorted_symbols[:limit]

def main():
    exchange = ccxt.binance({'enableRateLimit': True})
    top_symbols = get_top_currencies(exchange)
    selected_symbol = select_currency(exchange, top_symbols)

    if selected_symbol:
        print(f"Selected currency for trading: {selected_symbol}")
    else:
        print("No suitable currency found for trading.")

if __name__ == "__main__":
    main()
