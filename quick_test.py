from dotenv import load_dotenv
import os
import robin_stocks.robinhood as r
from utils.account_data import global_account_data, update_global_account_data
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

def login_to_robinhood():
    username = os.getenv('ROBINHOOD_USERNAME')
    password = os.getenv('ROBINHOOD_PASSWORD')
    
    if not username or not password:
        raise Exception("ROBINHOOD_USERNAME or ROBINHOOD_PASSWORD not found in the environment variables.")
    
    r.login(username=username, password=password)

# Function to get all open positions (symbols)
def get_open_position_symbols():
    positions = global_account_data.get('positions', {})
    open_position_symbols = [symbol for symbol in positions]
    print("Open Position Symbols:")
    print(open_position_symbols)
    return open_position_symbols

# Function to get all stock orders and filter those matching open positions
def get_stock_orders_and_match_open_positions(open_position_symbols):
    all_orders = r.orders.get_all_stock_orders()
    print("Stock Orders (Matching Open Positions):")
    
    matched_orders = {}

    if all_orders:
        for order in all_orders:
            instrument_url = order.get('instrument')
            
            if instrument_url:
                instrument_data = r.stocks.get_instrument_by_url(instrument_url)
                stock_symbol = instrument_data.get('symbol')
                
                if stock_symbol in open_position_symbols:
                    created_at = order.get('created_at', 'N/A')
                    print(f"Order for {stock_symbol}: Created at {created_at}")
                    matched_orders[stock_symbol] = created_at  # Store symbol and its creation date
            else:
                print("No instrument URL found in order.")
    else:
        print("No stock orders found.")
    
    return matched_orders

# Function to update the global account data with the created_at dates for positions
def update_global_account_data_with_dates(matched_symbols_dict):
    positions = global_account_data.get('positions', {})

    for symbol, created_at in matched_symbols_dict.items():
        if symbol in positions:
            # Update the global account data to add the creation date
            positions[symbol]['created_at'] = created_at

    global_account_data['positions'] = positions  # Update the global data with the modified positions

if __name__ == "__main__":
    login_to_robinhood()
    update_global_account_data()  # This updates the global_account_data with the latest positions
    
    # Step 1: Get all open position symbols
    open_position_symbols = get_open_position_symbols()
    
    # Step 2: Match open position symbols with all stock orders and print the matches
    matched_symbols_dict = get_stock_orders_and_match_open_positions(open_position_symbols)

    # Step 3: Update global account data with the creation dates
    update_global_account_data_with_dates(matched_symbols_dict)

    # Step 4: Print the updated global account data
    print("\nUpdated Global Account Data:")
    import json
    print(json.dumps(global_account_data, indent=4))





    # Uncomment any of the tests below as needed
    # get_account_info()
    # get_portfolio_info()
    # get_open_orders()
    
    # Print positions bought within the last 10 days
    # print_positions_with_days_held()

    # Get and print open stock orders
    # get_open_stock_orders()

# The following functions are retained but commented out for now.

# def get_account_info():
#     account_info = r.profiles.load_account_profile()
#     print("Account Information:")
#     print(account_info)

# def get_portfolio_info():
#     portfolio_info = r.profiles.load_portfolio_profile()
#     print("Portfolio Information:")
#     print(portfolio_info)

# def get_open_orders():
#     open_orders = r.orders.get_all_open_stock_orders()
#     print("Raw Open Orders Data:")
#     print(open_orders)  # Debug: Show entire response
    
#     if open_orders:
#         print("Open Order IDs:")
#         for order in open_orders:
#             if 'id' in order:
#                 print(order['id'])  # Print only the 'id'
#             else:
#                 print("No 'id' found for order:", order)  # Debug if no 'id' exists
#     else:
#         print("No open orders found.")

# def test_print_global_account_data():
#     import json
#     print("Account Info:")
#     print(json.dumps(global_account_data['account_info'], indent=4))
    
#     print("\nPortfolio Info:")
#     print(json.dumps(global_account_data['portfolio_info'], indent=4))
    
#     print("\nPositions:")
#     print(json.dumps(global_account_data['positions'], indent=4))