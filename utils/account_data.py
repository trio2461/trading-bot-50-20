# utils/account_data.py
import robin_stocks.robinhood as r
import os
from dotenv import load_dotenv

# Load environment variables (like Robinhood username and password)
load_dotenv()

# account_data.py
global_account_data = {
    'risk_percent': 0.0,  # Track risk percentage globally
    'risk_dollar': 0.0    # Track risk in dollar terms
}

def update_risk_in_global_data(new_risk_percent, new_risk_dollar):
    global_account_data['risk_percent'] += new_risk_percent
    global_account_data['risk_dollar'] += new_risk_dollar

def reset_risk_in_global_data():
    global_account_data['risk_percent'] = 0.0
    global_account_data['risk_dollar'] = 0.0

def login_to_robinhood():
    username = os.getenv('ROBINHOOD_USERNAME')
    password = os.getenv('ROBINHOOD_PASSWORD')
    r.login(username=username, password=password)

def update_global_account_data():
    global global_account_data
    global_account_data['account_info'] = r.profiles.load_account_profile()
    global_account_data['portfolio_info'] = r.profiles.load_portfolio_profile()
    global_account_data['positions'] = r.account.build_holdings()

def test_print_global_account_data():
    # Print out the global account data to verify everything is working
    print("Account Info:")
    print(global_account_data['account_info'])
    print("\nPortfolio Info:")
    print(global_account_data['portfolio_info'])
    print("\nPositions:")
    print(global_account_data['positions'])

# Call this function at the start of your script to login and populate the global dictionary
login_to_robinhood()
update_global_account_data()
test_print_global_account_data()