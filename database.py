# database.py
import sqlite3
from datetime import datetime
import logging  # Import the logging module

DB_FILE = 'trades.db'

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler for logging
log_file = 'database.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Create a formatter and add it to the file handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

def init_db():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS trades
                          (symbol TEXT PRIMARY KEY,
                           purchase_price REAL,
                           purchase_time TEXT)''')
        conn.commit()
        conn.close()
        logger.info('Database initialized successfully')
    except Exception as e:
        logger.error(f'Error initializing database: {str(e)}')

def record_trade(symbol, purchase_price, purchase_time):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO trades (symbol, purchase_price, purchase_time)
                          VALUES (?, ?, ?)''', (symbol, purchase_price, purchase_time.isoformat()))
        conn.commit()
        conn.close()
        logger.info(f'Trade recorded for {symbol}')
    except Exception as e:
        logger.error(f'Error recording trade for {symbol}: {str(e)}')

def get_trade(symbol):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''SELECT purchase_price, purchase_time FROM trades WHERE symbol=?''', (symbol,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'purchase_price': row[0], 'purchase_time': datetime.fromisoformat(row[1])}
        return None
    except Exception as e:
        logger.error(f'Error fetching trade for {symbol}: {str(e)}')
        return None

def insert_trade(symbol, purchase_price, purchase_time):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''INSERT OR REPLACE INTO trades (symbol, purchase_price, purchase_time)
                          VALUES (?, ?, ?)''', (symbol, purchase_price, purchase_time.isoformat()))
        conn.commit()
        conn.close()
        logger.info(f'Trade recorded for {symbol}')
    except Exception as e:
        logger.error(f'Error recording trade for {symbol}: {str(e)}')

def get_trade_by_symbol(symbol):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''SELECT purchase_price, purchase_time FROM trades WHERE symbol=?''', (symbol,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {'purchase_price': row[0], 'purchase_time': datetime.fromisoformat(row[1])}
        return None
    except Exception as e:
        logger.error(f'Error fetching trade for {symbol}: {str(e)}')
        return None

def get_all_trades(symbol=None):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        if symbol:
            cursor.execute('''SELECT * FROM trades WHERE symbol=?''', (symbol,))
        else:
            cursor.execute('''SELECT * FROM trades''')
        rows = cursor.fetchall()
        conn.close()
        trade_data = []
        for row in rows:
            trade_data.append({'symbol': row[0], 'purchase_price': row[1], 'purchase_time': datetime.fromisoformat(row[2])})
        return trade_data
    except Exception as e:
        logger.error(f'Error fetching trades: {str(e)}')
        return []

def get_available_currencies():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''SELECT DISTINCT symbol FROM trades''')
        currencies = cursor.fetchall()
        conn.close()
        available_currencies = [{'symbol': currency[0], 'name': currency[0]} for currency in currencies]
        return available_currencies
    except Exception as e:
        logger.error(f'Error fetching available currencies: {str(e)}')
        return []
        
if __name__ == '__main__':
    init_db()
