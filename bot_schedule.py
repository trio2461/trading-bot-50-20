# Removed run_check_positions function

# bot_schedule.py
import schedule
import logging
import signal
import sys
from bot import main
from datetime import datetime, time as datetime_time
import time

logging.basicConfig(filename='bot_schedule.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def market_hours():
    now = datetime.now().time()
    market_open = datetime_time(9, 30)
    market_close = datetime_time(16, 0)
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

# Removed run_check_positions and its scheduling

def signal_handler(sig, frame):
    logging.info("Received termination signal. Shutting down...")
    logging.info("Scheduler stopped at: %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

logging.info("Scheduler started at: %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

schedule.every(1).minute.do(lambda: run_main() if market_hours() else None)
schedule.every(5).hours.do(lambda: run_main() if not market_hours() else None)

logging.info("Scheduler running...")

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        logging.error(f"Error in the scheduler loop: {e}")