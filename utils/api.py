# utils/api.py
import robin_stocks.robinhood as r
import os
import logging
import contextlib
import pandas as pd
from dotenv import load_dotenv  # Import the function to load environment variables
from utils.settings import SIMULATED, SIMULATED_PORTFOLIO_SIZE  # Import settings

load_dotenv()

def login_to_robinhood():
    username = os.getenv('ROBINHOOD_USERNAME')
    password = os.getenv('ROBINHOOD_PASSWORD')
    r.login(username=username, password=password)


def get_positions():
    # Get stock positions
    stock_positions = r.account.build_holdings()
    
    # Get crypto positions
    try:
        crypto_positions = r.crypto.get_crypto_positions()
        # Convert crypto positions to same format as stocks
        for position in crypto_positions:
            # Only include positions with non-zero quantity
            if position['quantity'] != "0.000000000000000000":
                symbol = position['currency']['code']
                quantity = float(position['quantity'])
                price = float(r.crypto.get_crypto_quote(symbol)['mark_price'])
                # Get cost basis if available, otherwise use current price
                try:
                    cost_basis = float(position['cost_bases'][0]['direct_cost_basis'])
                    average_buy_price = cost_basis / quantity if quantity > 0 else price
                except (IndexError, KeyError, ZeroDivisionError):
                    average_buy_price = price
                
                stock_positions[symbol] = {
                    'name': symbol,
                    'quantity': str(quantity),
                    'price': str(price),
                    'average_buy_price': str(average_buy_price),
                    'equity': str(quantity * price),
                    'percent_change': str(((price - average_buy_price) / average_buy_price) * 100),
                    'equity_change': str((price - average_buy_price) * quantity),
                    'type': 'crypto'
                }
    except Exception as e:
        print(f"Error fetching crypto positions: {e}")
    
    print(f"Current Positions: {stock_positions}")
    return stock_positions

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


def order_crypto_buy_market(symbol, quantity):
    try:
        order = r.orders.order_buy_crypto_by_quantity(
            symbol=symbol,
            quantity=quantity
        )
        return order.get('id')
    except Exception as e:
        print(f"Error placing crypto market order: {e}")
        return None

def order_crypto_sell_market(symbol, quantity):
    try:
        order = r.orders.order_sell_crypto_by_quantity(
            symbol=symbol,
            quantity=quantity
        )
        return order
    except Exception as e:
        print(f"Error placing crypto market sell order: {e}")
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

def fetch_crypto_historical_data(symbol, interval='day', span='3month'):
    try:
        with contextlib.redirect_stdout(None):
            data = r.crypto.get_crypto_historicals(symbol, interval=interval, span=span)
        return data
    except Exception as e:
        logging.error(f"Failed to fetch crypto data for {symbol}: {e}")
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

