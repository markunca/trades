import subprocess
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from .config import SYMBOLS
from .database import init_db
from .trading import trade_currency

# Initialize a logger for the executor
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a file handler for logging
log_file = 'executor.log'
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Create a formatter and add it to the file handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

def start_flask_app():
    try:
        # Specify the command to run your Flask application (update paths as needed)
        flask_command = ["python", "/path/to/app.py"]

        # Start the Flask application as a separate process
        flask_process = subprocess.Popen(flask_command)

        # Log that the Flask application has been started
        logger.info("Flask web application started successfully")

        # Optionally, you can wait for the Flask process to finish
        flask_process.wait()
    except Exception as e:
        # Handle any errors that may occur when starting the Flask application
        logger.error(f"Error starting Flask web application: {str(e)}")

def execute_trades():
    try:
        # Start the Flask web application as a separate process
        start_flask_app()

        # Initialize the database
        init_db()

        # Trading bot logic using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=len(SYMBOLS)) as executor:
            futures = {executor.submit(trade_currency, symbol): symbol for symbol in SYMBOLS}
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    future.result()
                    logger.info(f"Completed trading for {symbol}")
                except Exception as exc:
                    logger.error(f"{symbol} generated an exception: {exc}")
                
                # Add a delay between symbol trades if needed
                time.sleep(5)  # Adjust the delay time as needed
    except KeyboardInterrupt:
        # Handle a keyboard interrupt (e.g., Ctrl+C)
        logger.info("Executor interrupted by the user")
    except Exception as e:
        # Handle any other exceptions that may occur during execution
        logger.error(f"Error in executor: {str(e)}")

if __name__ == '__main__':
    execute_trades()
