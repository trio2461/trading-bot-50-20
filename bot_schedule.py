import schedule
import time
import logging
import signal
import sys

# Import your bot's main logic
from bot import main

# Set up logging
logging.basicConfig(filename='bot_schedule.log', level=logging.INFO)

def job():
    try:
        logging.info("Running scheduled bot job...")
        main()  # This will run your bot's main function
    except Exception as e:
        logging.error(f"Error during scheduled job: {e}")

def signal_handler(sig, frame):
    logging.info("Received termination signal. Shutting down...")
    sys.exit(0)

# Register signal handlers for SIGINT (Ctrl+C) and SIGTERM
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Run every minute (for testing purposes)
schedule.every(1).minute.do(job)

# Uncomment this when you're ready to switch to an hourly schedule
# schedule.every().hour.do(job)

logging.info("Scheduler started...")

# Keep the scheduling running
while True:
    schedule.run_pending()
    time.sleep(1)