# quick_test.py is a script for testing the Robinhood API and the global account data.
from dotenv import load_dotenv
import os
import robin_stocks.robinhood as r
from utils.account_data import global_account_data, update_global_account_data
import json

# Load environment variables from .env file
load_dotenv()

def login_to_robinhood():
    try:
        username = os.getenv('ROBINHOOD_USERNAME')
        password = os.getenv('ROBINHOOD_PASSWORD')
        
        if not username or not password:
            raise Exception("ROBINHOOD_USERNAME or ROBINHOOD_PASSWORD not found in environment variables")
        
        login = r.login(username=username, password=password)
        print("Successfully logged into Robinhood")
        return login
    except Exception as e:
        print(f"Error logging in: {e}")
        return None

def get_account_info():
    account_info = r.profiles.load_account_profile()
    print("Account Information:")
    print(account_info)

def get_portfolio_info():
    portfolio_info = r.profiles.load_portfolio_profile()
    print("Portfolio Information:")
    print(portfolio_info)

def get_positions():
    positions = r.account.build_holdings()
    print("Current Positions:")
    print(positions)

def get_crypto_positions():
    try:
        crypto_positions = r.crypto.get_crypto_positions()
        print("\nCrypto Positions:")
        print(json.dumps(crypto_positions, indent=4))
        return crypto_positions
    except Exception as e:
        print(f"Error getting crypto positions: {e}")
        return None

def get_open_orders():
    open_orders = r.orders.get_all_open_stock_orders()
    print("Raw Open Orders Data:")
    print(open_orders)  # Debug: Show entire response
    
    if open_orders:
        print("Open Order IDs:")
        for order in open_orders:
            if 'id' in order:
                print(order['id'])  # Print only the 'id'
            else:
                print("No 'id' found for order:", order)  # Debug if no 'id' exists
    else:
        print("No open orders found.")

def test_print_global_account_data():
    try:
        print("\nGlobal Account Data:")
        print("Portfolio Value:", global_account_data.get('portfolio_info', {}).get('equity', 'N/A'))
        print("Buying Power:", global_account_data.get('account_info', {}).get('buying_power', 'N/A'))
    except Exception as e:
        print(f"Error printing global account data: {e}")

if __name__ == "__main__":
    print("Starting quick test...")
    if login_to_robinhood():
        update_global_account_data()
        test_print_global_account_data()
        print("\nQuick test completed successfully")
