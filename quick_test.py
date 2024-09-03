# quick_test.py
import robin_stocks.robinhood as r

def login_to_robinhood():
    r.login(username="your_username", password="your_password")

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

def get_open_positions():  # Renamed from get_open_orders
    open_positions = r.account.get_open_stock_positions()
    print("Open Positions:")
    print(open_positions)

if __name__ == "__main__":
    login_to_robinhood()
    get_open_positions()