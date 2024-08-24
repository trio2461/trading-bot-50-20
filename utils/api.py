import robin_stocks.robinhood as r
import os
import logging
import contextlib
import pandas as pd

def login_to_robinhood():
    username = os.getenv('ROBINHOOD_USERNAME')
    password = os.getenv('ROBINHOOD_PASSWORD')
    r.login(username=username, password=password)

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

def get_portfolio_size(simulated=True, simulated_size=1000):
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
