import ccxt
import logging
from datetime import datetime, timedelta
import pandas as pd
from config import *
from database import *
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
        record_trade(
            symbol=symbol,
            currency='USD',  # or the actual currency you're using
            created_at=datetime.now(),
            amount=calculated_amount,  # you need to define how you get this value
            buy_price=last_row['close'],
            buy_cost=amount * last_row['close'],  # assuming cost = amount * price
            sell_price=0,  # since it's a buy, sell_price and sell_cost are not applicable
            sell_cost=0,
            provision_buy=0,  # TBD by binance
            provision_sell=0,  # since it's a buy, no sell provision
            profit=0,  # profit is calculated after selling
            wallet_status='buy',  # or however you track wallet status
            pnl_percentage=0  # since it's a buy, pnl_percentage is not applicable
        )
    elif sell_condition and last_trade and last_trade['type'] == 'buy':
        logger.info(f"Sell signal for {symbol}")
        # Uncomment to execute a sell order on Binance
        # exchange.create_market_sell_order(symbol, calculated_amount)

        provision_sell = 0 #TBD provision of sale
        
        update_trade(
            trade_id=last_trade['id'],
            sell_price=last_row['close'],
            sell_cost=amount * last_row['close'],  # assuming cost = amount * price
            provision_sell=provision_sell,  # you need to define how you calculate this
            profit=(last_row['close'] - buy_price) * amount - provision_sell - provision_buy,  # example profit calculation
            wallet_status='sell',  # or however you track wallet status after selling
            pnl_percentage=((last_row['close'] / buy_price) - 1) * 100  # example pnl calculation
            # You might also need to update other fields depending on your logic
        )

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
