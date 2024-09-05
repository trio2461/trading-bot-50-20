import schedule
import time
import logging
import signal
import sys
from bot import main
from utils.trading import check_open_positions_sell_points
from datetime import datetime

logging.basicConfig(filename='bot_schedule.log', level=logging.INFO)

def market_hours():
    now = datetime.now().time()
    market_open = time(9, 30)  # Market open time
    market_close = time(16, 0)  # Market close time
    return market_open <= now <= market_close

def run_main():
    if market_hours():
        logging.info("Running main every minute during market hours...")
        main()
    else:
        logging.info("Running main every 5 hours during non-market hours...")

def run_check_positions():
    if market_hours():
        logging.info("Checking positions every 5 minutes during market hours...")
        check_open_positions_sell_points()
    else:
        logging.info("Checking positions every 5 hours during non-market hours...")

def signal_handler(sig, frame):
    logging.info("Received termination signal. Shutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Schedule tasks for market hours (9:30 AM - 4:00 PM)
schedule.every(1).minute.do(lambda: run_main() if market_hours() else None)  # Runs main every minute during market hours
schedule.every(5).minutes.do(lambda: run_check_positions() if market_hours() else None)  # Runs check positions every 5 minutes during market hours

# Schedule tasks for non-market hours
schedule.every(5).hours.do(lambda: run_main() if not market_hours() else None)  # Runs main every 5 hours during non-market hours
schedule.every(5).hours.do(lambda: run_check_positions() if not market_hours() else None)  # Runs check positions every 5 hours during non-market hours

logging.info("Scheduler started...")

while True:
    schedule.run_pending()
    time.sleep(1)
