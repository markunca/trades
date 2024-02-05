# trading.py
import ccxt
from datetime import datetime, timedelta
from config import *
from database import get_trade, record_trade
from indicators import calculate_indicators
from utils import fetch_data
import logging  # Import the logging module

binance = ccxt.binance({
    'apiKey': API_KEY,
    'secret': SECRET_KEY
})

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler for logging
log_file = 'trading.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Create a formatter and add it to the file handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

def trade_currency(symbol):
    try:
        # Dynamically calculate 'since_period' for data fetching
        since_period = datetime.utcnow() - timedelta(hours=LOOKBACK_PERIOD * TIMEFRAME_IN_HOURS)
        since_timestamp = binance.parse8601(since_period.strftime('%Y-%m-%dT%H:%M:%SZ'))

        # Fetch and process data
        df = fetch_data(symbol, TIMEFRAME, binance.parse8601(SINCE_PERIOD))
        df = calculate_indicators(df)
        last_row = df.iloc[-1]

        # Trading logic
        trade = get_trade(symbol)
        if not trade:
            if last_row['RSI'] < RSI_THRESHOLD and last_row['stoch_rsi'] < STOCH_RSI_THRESHOLD and last_row['close'] < last_row['daily_avg']:
                print(f"Executing buy for {symbol} at {last_row['close']}")
                # Uncomment the following line to execute a real buy order
                # binance.create_market_buy_order(symbol, amount_to_trade)
                record_trade(symbol, last_row['close'], datetime.now())
                logger.info(f'Buy executed for {symbol} at {last_row["close"]}')
        elif check_sell_conditions(last_row, last_row['close'], trade['purchase_price']):
            print(f"Executing sell for {symbol} at {last_row['close']}")
            # Uncomment the following line to execute a real sell order
            # binance.create_market_sell_order(symbol, amount_to_trade)
            logger.info(f'Sell executed for {symbol} at {last_row["close"]}')
    except Exception as e:
        logger.error(f'Error trading {symbol}: {str(e)}')
