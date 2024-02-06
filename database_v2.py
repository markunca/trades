import mariadb
import sys
import logging
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'user': 'your_user',
    'password': 'your_password',
    'host': 'localhost',
    'port': 3306,
    'database': 'your_database'
}

# Initialize logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('database.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Establish a database connection
def connect_db():
    try:
        conn = mariadb.connect(**DB_CONFIG)
        return conn
    except mariadb.Error as e:
        logger.error(f"Error connecting to MariaDB: {e}")
        sys.exit(1)

# Initialize the database
def init_db():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INT AUTO_INCREMENT PRIMARY KEY,
                symbol VARCHAR(10),
                currency VARCHAR(10),
                created_at DATETIME,
                amount DECIMAL(16,8),
                buy_price DECIMAL(16,8),
                buy_cost DECIMAL(16,8),
                sell_price DECIMAL(16,8),
                sell_cost DECIMAL(16,8),
                provision_sell DECIMAL(16,8),
                provision_buy DECIMAL(16,8),
                profit DECIMAL(16,8),
                wallet_status VARCHAR(50),
                pnl_percentage DECIMAL(5,2)
            )
        ''')
        conn.commit()
    except mariadb.Error as e:
        logger.error(f"Error initializing database: {e}")
    finally:
        cur.close()
        conn.close()
# Continue from the previous code snippet...

# Record a new trade
def record_trade(symbol, currency, created_at, amount, buy_price, buy_cost, sell_price, sell_cost, provision_sell, provision_buy, profit, wallet_status, pnl_percentage):
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO trades (symbol, currency, created_at, amount, buy_price, buy_cost, sell_price, sell_cost, provision_sell, provision_buy, profit, wallet_status, pnl_percentage)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (symbol, currency, created_at, amount, buy_price, buy_cost, sell_price, sell_cost, provision_sell, provision_buy, profit, wallet_status, pnl_percentage))
        conn.commit()
    except mariadb.Error as e:
        logger.error(f"Error recording trade: {e}")
    finally:
        cur.close()
        conn.close()

# Fetch a specific trade by ID
def get_trade(trade_id):
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM trades WHERE id = %s", (trade_id,))
        trade = cur.fetchone()
        return trade
    except mariadb.Error as e:
        logger.error(f"Error fetching trade {trade_id}: {e}")
    finally:
        cur.close()
        conn.close()

# Update a trade record
def update_trade(trade_id, **kwargs):
    conn = connect_db()
    try:
        cur = conn.cursor()
        columns = ', '.join(f"{k} = %s" for k in kwargs)
        values = list(kwargs.values())
        values.append(trade_id)
        cur.execute(f"UPDATE trades SET {columns} WHERE id = %s", values)
        conn.commit()
    except mariadb.Error as e:
        logger.error(f"Error updating trade {trade_id}: {e}")
    finally:
        cur.close()
        conn.close()

# Delete a trade record
def delete_trade(trade_id):
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM trades WHERE id = %s", (trade_id,))
        conn.commit()
    except mariadb.Error as e:
        logger.error(f"Error deleting trade {trade_id}: {e}")
    finally:
        cur.close()
        conn.close()

# Retrieve all trades for a specific currency
def get_trades_by_currency(currency):
    conn = connect_db()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM trades WHERE currency = %s", (currency,))
        trades = cur.fetchall()
        return trades
    except mariadb.Error as e:
        logger.error(f"Error fetching trades for currency {currency}: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    init_db()
