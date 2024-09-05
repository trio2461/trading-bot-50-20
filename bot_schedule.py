import schedule
import logging
import signal
import sys
from bot import main
from utils.trading import check_open_positions_sell_points
from datetime import datetime, time as datetime_time
import time  # This is the correct 'time' module for sleep

# Set up logging
logging.basicConfig(filename='bot_schedule.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def market_hours():
    now = datetime.now().time()
    market_open = datetime_time(9, 30)  # Use the correct 'time' class from datetime
    market_close = datetime_time(16, 0)  # Use the correct 'time' class from datetime
    return market_open <= now <= market_close

def run_main():
    try:
        if market_hours():
            logging.info("Running main every minute during market hours...")
            main()
        else:
            logging.info("Running main every 5 hours during non-market hours...")
    except Exception as e:
        logging.error(f"Error occurred during run_main: {e}")

def run_check_positions():
    try:
        if market_hours():
            logging.info("Checking positions every 5 minutes during market hours...")
            check_open_positions_sell_points()
        else:
            logging.info("Checking positions every 5 hours during non-market hours...")
    except Exception as e:
        logging.error(f"Error occurred during run_check_positions: {e}")

def signal_handler(sig, frame):
    logging.info("Received termination signal. Shutting down...")
    logging.info("Scheduler stopped at: %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Log the start time and date when the scheduler starts
logging.info("Scheduler started at: %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# Schedule tasks for market hours (9:30 AM - 4:00 PM)
schedule.every(1).minute.do(lambda: run_main() if market_hours() else None)
schedule.every(5).minutes.do(lambda: run_check_positions() if market_hours() else None)

# Schedule tasks for non-market hours
schedule.every(5).hours.do(lambda: run_main() if not market_hours() else None)
schedule.every(5).hours.do(lambda: run_check_positions() if not market_hours() else None)

logging.info("Scheduler running...")

while True:
    try:
        schedule.run_pending()
        time.sleep(1)  # Now correctly using the time module for sleep
    except Exception as e:
        logging.error(f"Error in the scheduler loop: {e}")