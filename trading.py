import ccxt
import logging
from datetime import datetime, timedelta
import pandas as pd
from config import *
from database import get_trade, record_trade, update_trade
from utils import fetch_data
from indicators import calculate_indicators
import currency_selection  # Ensure this module is correctly implemented

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the exchange
exchange = ccxt.binance({
    'apiKey': API_KEY,
    'secret': SECRET_KEY,
    'enableRateLimit': True,
})

def execute_trade(symbol, df):
    """
    Execute a trade based on calculated indicators from indicators.py.
    :param symbol: Symbol to trade.
    :param df: DataFrame with indicators and price data.
    """
    last_row = df.iloc[-1]
    last_trade = get_trade(symbol)

    # Define buy/sell conditions based on indicators.py logic
    buy_condition = last_row['RSI'] < df['RSI'].mean() - df['RSI'].std() and (last_trade is None or last_trade['type'] == 'sell')
    sell_condition = last_row['RSI'] > df['RSI'].mean() + df['RSI'].std() and last_trade and last_trade['type'] == 'buy'

    if buy_condition:
        logger.info(f"Buy signal for {symbol}")
        # Uncomment to execute a buy order on Binance
        # exchange.create_market_buy_order(symbol, amount)
        record_trade(symbol, 'buy', last_row['close'], datetime.now())
    elif sell_condition:
        logger.info(f"Sell signal for {symbol}")
        # Uncomment to execute a sell order on Binance
        # exchange.create_market_sell_order(symbol, amount)
        update_trade(last_trade['id'], 'sell', last_row['close'], datetime.now())

def run_trading_cycle():
    for symbol in SYMBOLS:
        logger.info(f"Analyzing {symbol} for trading opportunities")
        selected_symbol = currency_selection.select_currency(exchange, [symbol])

        if selected_symbol:
            data = fetch_data(selected_symbol, TIMEFRAME, datetime.now() - timedelta(days=LOOKBACK_PERIOD))
            df = calculate_indicators(pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']))
            execute_trade(selected_symbol, df)
        else:
            logger.info(f"No suitable currency found for trading in this cycle for {symbol}.")

if __name__ == '__main__':
    run_trading_cycle()
