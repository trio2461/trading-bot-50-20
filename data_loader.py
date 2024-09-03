# data_loader.py
from utils.api import sanitize_ticker_symbols
import pandas as pd
from utils.settings import USE_CSV_DATA, USE_NASDAQ_DATA, USE_SP500_DATA  # Import the settings

def load_stock_symbols():
    stock_symbols = []

    if USE_NASDAQ_DATA and not USE_SP500_DATA:
        nasdaq_data = load_csv_data('nasdaq100_full.csv', 'nasdaq')
        nasdaq_data = sanitize_ticker_symbols(nasdaq_data)  # Sanitize ticker symbols
        stock_symbols = nasdaq_data['Ticker'].tolist()
    elif USE_SP500_DATA and not USE_NASDAQ_DATA:
        sp500_data = load_csv_data('sp500_companies.csv', 'sp500')
        sp500_data = sanitize_ticker_symbols(sp500_data)  # Sanitize ticker symbols
        stock_symbols = sp500_data['Symbol'].tolist()
    elif USE_NASDAQ_DATA and USE_SP500_DATA:
        nasdaq_data = load_csv_data('nasdaq100_full.csv', 'nasdaq')
        nasdaq_data = sanitize_ticker_symbols(nasdaq_data)  # Sanitize ticker symbols
        sp500_data = load_csv_data('sp500_companies.csv', 'sp500')
        sp500_data = sanitize_ticker_symbols(sp500_data)  # Sanitize ticker symbols
        stock_symbols = nasdaq_data['Ticker'].tolist() + sp500_data['Symbol'].tolist()

    return stock_symbols

def load_csv_data(file_path, exchange):
    df = pd.read_csv(file_path)
    if exchange.lower() == 'nasdaq':
        return df[['Ticker']]  
    elif exchange.lower() == 'sp500':
        return df[['Symbol']]  
    else:
        raise ValueError("Unsupported exchange. Please use 'nasdaq' or 'sp500'.")