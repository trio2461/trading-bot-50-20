Here’s a README for your project that includes the new scheduled task setup using Python's `schedule` library and instructions on stopping the bot:

---

# Trading Bot README

This project contains a Python-based trading bot that automatically checks and executes trades based on predefined strategies. It uses the `schedule` library to run the bot at specific times.

## Setup

1. **Environment Setup:**
   Make sure to install the required Python libraries by running:

    ```bash
    pip install -r requirements.txt
    ```

2. **Scheduled Execution:**
   The bot uses the `schedule` library to control when it runs. The scheduling can be customized in the `scheduled_bot.py` file.

    - The current setup runs the bot every minute (for testing purposes).
    - When ready, you can uncomment the hourly schedule and adjust the frequency.

3. **Running the Bot:**
   To start the bot manually, you can run:

    ```bash
    python scheduled_bot.py
    ```

    This will trigger the schedule and run the bot according to the configured timings in `scheduled_bot.py`.

4. **Stopping the Bot:**

    If the bot is running and you need to stop it, you can follow these steps:

    - **Find the process ID (PID):**
      Open a terminal and run the following command to list all Python processes:

        ```bash
        ps aux | grep python
        ```

        Look for the process that is running your bot (you should see the path to your bot file).

    - **Kill the process:**
      Once you identify the PID (e.g., 1234), you can stop it by running:

        ```bash
        kill 1234
        ```

        If the process doesn’t stop, you can force kill it:

        ```bash
        kill -9 1234
        ```

        Alternatively, if the bot is running in a terminal session, you can stop it by pressing `Ctrl + C` in the terminal window.

5. **Log File:**
   All actions of the bot are logged in `bot_schedule.log`, so you can review the bot's activity.

---

### Example of Scheduling Setup:

-   **Every minute (for testing):**

    ```python
    schedule.every(1).minutes.do(run_bot)
    ```

-   **Every hour on weekdays from 9:30 AM to 4 PM and every 5 hours on weekends:**

    ```python
    schedule.every().monday.at("09:30").do(run_bot)
    schedule.every().tuesday.at("09:30").do(run_bot)
    schedule.every().wednesday.at("09:30").do(run_bot)
    schedule.every().thursday.at("09:30").do(run_bot)
    schedule.every().friday.at("09:30").do(run_bot)

    schedule.every(1).hour.until("16:00").do(run_bot)

    # Weekend scheduling
    schedule.every(5).hours.do(run_bot)
    ```

---

With this README, you'll have the instructions you need for setting up, running, and stopping the bot. Let me know if you want further adjustments!
