# utils/api.py
import robin_stocks.robinhood as r
import os
import logging
import contextlib
import pickle
import pandas as pd
from dotenv import load_dotenv  # Import the function to load environment variables
from utils.settings import SIMULATED, SIMULATED_PORTFOLIO_SIZE  # Import settings
# Load environment variables (ROBINHOOD_USERNAME and ROBINHOOD_PASSWORD)
load_dotenv()

# Set up logging
logging.basicConfig(filename='robinhood_login.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Path to save the login session
PICKLE_NAME = 'robinhood_session.pkl'

def save_session(session_data):
    """Save the session data to a pickle file."""
    with open(PICKLE_NAME, 'wb') as f:
        pickle.dump(session_data, f)
    print(f"Session data saved to {PICKLE_NAME}.")

def load_session():
    """Load the session data from a pickle file."""
    if os.path.exists(PICKLE_NAME):
        with open(PICKLE_NAME, 'rb') as f:
            session_data = pickle.load(f)
            r.authentication.set_login_state(session_data)
            print(f"Session data loaded from {PICKLE_NAME}.")
            return True
    return False

def login_to_robinhood():
    # Attempt to load a saved session
    if load_session():
        print("Session loaded. No need to log in again.")
        return

    username = os.getenv('ROBINHOOD_USERNAME')
    password = os.getenv('ROBINHOOD_PASSWORD')

    if not username or not password:
        logging.error("Username or password not found in environment variables.")
        print("Username or password not found in environment variables.")
        return None

    try:
        print(f"Attempting to log in with Username: {username}")

        # Prompt for MFA code, but allow skipping by pressing Enter
        mfa_code = input("Enter MFA code (if needed, otherwise press Enter to skip): ").strip()

        # Log in to Robinhood
        login_data = r.authentication.login(
            username=username,
            password=password,
            mfa_code=mfa_code if mfa_code else None,
            store_session=False  # We will manually handle session saving
        )

        # Check if login was successful
        if 'access_token' in login_data:
            print("Login successful!")
            logging.info("Login successful!")

            # Manually save the session data
            save_session(r.authentication.get_login_state())
            return login_data
        else:
            print(f"Login failed: {login_data}")
            logging.error(f"Login failed: {login_data}")
            return None

    except Exception as e:
        print(f"Login failed: {e}")
        logging.error(f"Login failed: {e}")
        return None

def order_buy_market(symbol, quantity):
    try:
        order = r.orders.order_buy_market(symbol, quantity)
        order_id = order.get('id')  # Extract the order ID from the response
        return order_id
    except Exception as e:
        print(f"Error placing market order: {e}")
        return None


def order_sell_market(symbol, quantity):
    try:
        order = r.orders.order_sell_market(symbol, quantity)
        return order
    except Exception as e:
        print(f"Error placing market sell order: {e}")
        return None


def fetch_historical_data(stock, interval='day', span='3month'):
    try:
        sanitized_stock = stock.replace('-', '')
        with contextlib.redirect_stdout(None):  # Suppress console output
            data = r.stocks.get_stock_historicals(sanitized_stock, interval=interval, span=span)
        return data
    except (r.exceptions.APIError, r.exceptions.RequestError, r.exceptions.NotFound) as e:
        logging.error(f"Failed to fetch data for {stock}: {e}")
        return None


def get_top_movers(direction='up'):
    try:
        movers = r.markets.get_top_movers_sp500(direction=direction)
        symbols = [mover['symbol'] for mover in movers]
        return symbols
    except Exception as e:
        logging.error(f"Failed to fetch top movers: {e}")
        return []


def get_portfolio_size(simulated=SIMULATED, simulated_size=SIMULATED_PORTFOLIO_SIZE):  # Use settings for defaults
    if simulated:
        return simulated_size
    else:
        portfolio = r.profiles.load_account_profile(info='portfolio_cash')
        return float(portfolio)


def load_csv_data(file_path, exchange):
    df = pd.read_csv(file_path)
    if exchange.lower() == 'nasdaq':
        return df[['Ticker']]  # Use 'Ticker' for NASDAQ
    elif exchange.lower() == 'sp500':
        return df[['Symbol']]  # Use 'Symbol' for S&P 500
    else:
        raise ValueError("Unsupported exchange. Please use 'nasdaq' or 'sp500'.")


def sanitize_ticker_symbols(df):
    """
    Sanitizes ticker symbols in the DataFrame.

    :param df: DataFrame containing the data.
    :return: DataFrame with sanitized ticker symbols.
    """
    column_name = df.columns[0]  # Assume first column contains ticker symbols
    df[column_name] = df[column_name].str.replace('-', '', regex=True)  # Remove hyphens
    df[column_name] = df[column_name].str.strip()  # Remove leading/trailing spaces
    df[column_name] = df[column_name].str.upper()  # Convert to uppercase for consistency
    return df

 