import ccxt
import logging
from datetime import datetime, timedelta
from config import *
from database import get_trade, record_trade
from indicators import calculate_indicators
from utils import fetch_data

# Setup logging
logging.basicConfig(level=logging.INFO, filename='trading.log',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger(__name__)

binance = ccxt.binance({'apiKey': API_KEY, 'secret': SECRET_KEY})

def fetch_and_prepare_data(symbol, lookback_period, timeframe):
    logger.debug(f'Fetching data for {symbol}')
    since_period = datetime.utcnow() - timedelta(hours=lookback_period * timeframe)
    since_timestamp = binance.parse8601(since_period.strftime('%Y-%m-%dT%H:%M:%SZ'))
    df = fetch_data(symbol, TIMEFRAME, since_timestamp)
    logger.debug(f'Data fetched for {symbol}, calculating indicators')
    df = calculate_indicators(df)
    return df

def evaluate_trade_conditions(df, symbol):
    last_row = df.iloc[-1]
    trade = get_trade(symbol)
    if trade:
        return check_sell_conditions(last_row, last_row['close'], trade['purchase_price'])
    else:
        return last_row['RSI'] < RSI_THRESHOLD and last_row['stoch_rsi'] < STOCH_RSI_THRESHOLD and last_row['close'] < last_row['daily_avg']

def execute_trade(action, symbol, price):
    logger.info(f'{action.capitalize()} executed for {symbol} at {price}')
    # Uncomment the next lines to execute real orders
    # if action == 'buy':
    #     binance.create_market_buy_order(symbol, amount_to_trade)
    # elif action == 'sell':
    #     binance.create_market_sell_order(symbol, amount_to_trade)
    record_trade(symbol, price, datetime.now())

def trade_currency(symbol):
    try:
        df = fetch_and_prepare_data(symbol, LOOKBACK_PERIOD, TIMEFRAME_IN_HOURS)
        if evaluate_trade_conditions(df, symbol):
            last_row = df.iloc[-1]
            action = 'sell' if get_trade(symbol) else 'buy'
            execute_trade(action, symbol, last_row['close'])
    except Exception as e:
        logger.error(f'Error trading {symbol}: {str(e)}', exc_info=True)

if __name__ == '__main__':
    # Example usage: trade_currency('BTC/USDT')
    trade_currency(SYMBOL_TO_TRADE)
