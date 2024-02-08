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
    Execute a trade based on calculated indicators.
    :param symbol: Symbol to trade.
    :param df: DataFrame with indicators and price data.
    """
    last_row = df.iloc[-1]
    last_trade = get_trade(symbol)

    # Define buy/sell conditions based on the indicators' logic
    buy_condition = last_row['RSI'] < 30  # Example buy condition based on RSI
    sell_condition = last_row['RSI'] > 70  # Example sell condition based on RSI

    if buy_condition and (last_trade is None or last_trade['type'] == 'sell'):
        logger.info(f"Buy signal for {symbol}")
        # Uncomment to execute a buy order on Binance
        # exchange.create_market_buy_order(symbol, calculated_amount)
        record_trade(symbol, 'buy', last_row['close'], datetime.now())
    elif sell_condition and last_trade and last_trade['type'] == 'buy':
        logger.info(f"Sell signal for {symbol}")
        # Uncomment to execute a sell order on Binance
        # exchange.create_market_sell_order(symbol, calculated_amount)
        update_trade(last_trade['id'], 'sell', last_row['close'], datetime.now())

def run_trading_cycle():
    top_symbols = currency_selection.get_top_currencies(exchange)  # Get top currencies based on volume
    selected_symbol = currency_selection.select_currency(exchange, top_symbols)  # Select the best currency

    if selected_symbol:
        logger.info(f"Selected currency for trading: {selected_symbol}")
        data = fetch_data(selected_symbol, TIMEFRAME, datetime.now() - timedelta(days=LOOKBACK_PERIOD))
        df = calculate_indicators(pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']))
        execute_trade(selected_symbol, df)
    else:
        logger.info("No suitable currency found for trading in this cycle.")

if __name__ == '__main__':
    run_trading_cycle()
