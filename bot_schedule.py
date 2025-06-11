import schedule
import logging
import signal
import sys
from bot import main  # Ensure this is importing the correct 'main' function
from datetime import datetime
import time
import os
import subprocess

# Setup logging
logging.basicConfig(filename='bot_schedule.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure any previous 'bot_schedule.py' processes are killed
def kill_existing_process():
    try:
        result = subprocess.run(['pgrep', '-f', 'bot_schedule.py'], stdout=subprocess.PIPE)
        pids = result.stdout.decode().strip().split('\n')
        for pid in pids:
            if pid and int(pid) != os.getpid():
                print(f"Killing existing bot_schedule.py process with PID: {pid}")
                os.kill(int(pid), signal.SIGTERM)
                logging.info(f"Killed existing bot_schedule.py process with PID: {pid}")
    except Exception as e:
        logging.error(f"Error killing existing process: {e}")
        print(f"Error killing existing process: {e}")

kill_existing_process()

# Debugging Helper
def log_and_print(message):
    print(message)
    logging.info(message)

# Signal handling for termination
def signal_handler(sig, frame):
    log_and_print("Received termination signal. Shutting down...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Main function to run bot logic
def run_main():
    try:
        log_and_print("Running bot's main() function...")
        main()  # Call to bot.py's main function
    except Exception as e:
        logging.error(f"Error in run_main: {e}")
        print(f"Error in run_main: {e}")

# Scheduler setup
log_and_print("Starting bot scheduler...")

# For testing, we are running every 30 seconds (you can switch this to 5 minutes)
# schedule.every(59).seconds.do(run_main)

# # Uncomment for production
schedule.every(15).minutes.do(run_main)

# Scheduler loop
while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        logging.error(f"Error in the scheduler loop: {e}")
        print(f"Error in the scheduler loop: {e}")