Here's an updated `README.md` that includes your project tree and the Python version requirement:

---

# Trading Bot

This is a stock trading bot designed to analyze stock data, identify trading opportunities based on technical analysis (e.g., ATR and moving average crossovers), and execute trades on the Robinhood platform. The bot centralizes all data related to account, portfolio, and positions in a single dictionary (`global_account_data`) to ensure consistency and simplify data management across the project.

## Features

-   **Centralized Data Dictionary**: All account, portfolio, and position information is stored in a single dictionary (`global_account_data`) for easy access across the application.
-   **Technical Analysis**: The bot uses ATR (Average True Range) and moving average crossovers to analyze stock data and identify trading opportunities.
-   **Automated Trading**: Executes trades on the Robinhood platform based on the analysis.
-   **Simulated and Live Trading**: Supports both simulated and live trading modes.
-   **Risk Management**: Implements risk management, limiting the risk per trade and maximum daily loss.

## Project Structure

Below is the project structure for the trading bot:

```
.
├── __init__.py
├── __pycache__
│   ├── bot.cpython-312.pyc
│   ├── data_loader.cpython-312.pyc
│   └── logger.cpython-312.pyc
├── bot.py                     # Main bot logic
├── bot_schedule.log            # Log file for scheduled jobs
├── bot_schedule.py             # Scheduler for running the bot during market hours
├── close_all_positions.py      # Script to close all positions
├── combined_minified.py        # Combined and minified Python code
├── data_loader.py              # Load stock symbols from CSV or API
├── error_log.txt               # Log file for errors
├── gpt.py                      # Script to minify and combine code files
├── logger.py                   # Logs key actions and events
├── nasdaq100_full-.csv          # Example CSV data (NASDAQ 100 stocks)
├── nasdaq100_full.csv           # Example CSV data (NASDAQ 100 stocks)
├── quick_test.py               # Script for testing account data
├── readmes
│   ├── initial-setup.md        # Setup instructions
│   ├── risk-formula.md         # Explanation of the risk management formula
│   ├── robinhood.md            # Robinhood API instructions
│   ├── scheduler.md            # Scheduler details
│   └── to-do.md                # To-do list for the project
├── requirements.txt            # List of Python dependencies
├── sp500_companies.csv         # Example CSV data (S&P 500 companies)
└── utils                       # Utility functions and modules
    ├── __init__.py
    ├── __pycache__
    │   ├── __init__.cpython-312.pyc
    │   ├── account_data.cpython-312.pyc
    │   ├── analysis.cpython-312.pyc
    │   ├── api.cpython-312.pyc
    │   ├── send_message.cpython-312.pyc
    │   ├── settings.cpython-312.pyc
    │   ├── trade_state.cpython-312.pyc
    │   └── trading.cpython-312.pyc
    ├── account_data.py         # Functions to manage global account data
    ├── analysis.py             # Technical analysis functions (ATR, moving averages)
    ├── api.py                  # API interactions with Robinhood
    ├── send_message.py         # iMessage integration for sending trade summaries
    ├── settings.py             # Configuration settings (e.g., simulated mode)
    ├── trade_state.py          # Trade state management and risk calculation
    └── trading.py              # Stock analysis and trade execution
```

## How It Works

1. **Fetch Account and Portfolio Data**: The bot retrieves and stores account and portfolio data in `global_account_data`.
2. **Analyze Stocks**: The bot analyzes a list of stocks using ATR and moving averages, checking for eligible trades.
3. **Execute Trades**: If a stock meets the trading criteria, the bot places the trade.
4. **Track Risk**: The bot calculates and tracks the risk based on open trades to avoid exceeding the maximum daily loss.
5. **Send Trade Summary**: A trade summary is generated and can be sent via iMessage using AppleScript.

### Centralized Data Dictionary

The **`global_account_data`** dictionary stores all relevant data related to the account, portfolio, and positions, which simplifies access and reduces redundant code.

### Example of `global_account_data`:

```python
global_account_data = {
    'account_info': { 'url': 'https://api.robinhood.com/accounts/XXXX/' },
    'portfolio_info': { 'market_value': '2000.00' },
    'positions': { 'AAPL': { 'quantity': 10, 'average_buy_price': 150.00 } },
    'risk_percent': 0.05,
    'risk_dollar': 100.00,
    'sales': []
}
```

## Requirements

-   **Python Version**: This project requires **Python 3.12**.
-   **Dependencies**: The following Python libraries are required and listed in `requirements.txt`:
    -   `robin_stocks`
    -   `dotenv`
    -   `tqdm`
    -   `termcolor`

### Installation Steps

1. **Clone the Repository**:

    ```bash
    git clone https://github.com/yourusername/trading-bot.git
    cd trading-bot
    ```

2. **Set Up Python Virtual Environment**:

    ```bash
    python3.12 -m venv env
    source env/bin/activate
    ```

3. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Set Up `.env` File**:
   Create a `.env` file with your Robinhood credentials:

    ```
    ROBINHOOD_USERNAME=your_robinhood_username
    ROBINHOOD_PASSWORD=your_robinhood_password
    ```

5. **Run the Bot**:
    ```bash
    python3 bot.py
    ```

## Risk Management

The bot includes built-in risk management features:

-   **Max Daily Loss**: Limits the total daily loss to 6% of the portfolio value.
-   **Per-Trade Risk**: Limits the risk per trade to 2% of the portfolio value.

These values are configurable in `settings.py`.

## Logging and Debugging

-   **Logs**: Key actions are logged in the `bot_schedule.log` file.
-   **Error Handling**: Errors are captured and logged in `error_log.txt` for debugging purposes.

## To-Do

The project includes a `to-do.md` file in the `readmes` directory, which outlines future features and improvements.

---

This `README.md` provides clear guidance for setting up and using the trading bot with Python 3.12, including an overview of the project structure and centralized data dictionary design.
