# close_all_positions.py
import robin_stocks.robinhood as r
from dotenv import load_dotenv  # Import the function to load environment variables
import os

load_dotenv()

def login_to_robinhood():
	username = os.getenv('ROBINHOOD_USERNAME')
	password = os.getenv('ROBINHOOD_PASSWORD')
	r.login(username=username, password=password)

def close_all_positions():
    positions = r.account.build_holdings()
    for symbol, data in positions.items():
        quantity = float(data['quantity'])
        print(f"Closing position for {symbol} with {quantity} shares.")
        
        # Use the generic order function to specify all necessary parameters
        order = r.orders.order(
            symbol=symbol,
            quantity=quantity,
            side='sell',
            timeInForce='gfd',  # Good for Day
            market_hours='regular_hours'  # Regular market hours
        )
        
        print(f"Response from Robinhood: {order}")
        if 'id' in order:
            print(f"Position for {symbol} closed successfully.")
        else:
            print(f"Failed to close position for {symbol}. Response: {order}")

if __name__ == "__main__":
    login_to_robinhood()
    close_all_positions()
