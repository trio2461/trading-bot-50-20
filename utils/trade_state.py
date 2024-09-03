# utils/trade_state.py
import robin_stocks.robinhood as r
from datetime import datetime
from utils.analysis import calculate_atr
from utils.api import fetch_historical_data
from utils.account_data import global_account_data


class TradeState:
    def __init__(self, symbol, quantity, price, order_id, side, order_status="pending"):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.order_id = order_id
        self.side = side  
        self.order_status = order_status  
        self.trade_date = datetime.now()  
        self.risk = self.calculate_risk()
    
    def calculate_risk(self):
        return self.quantity
    
    def is_expired(self, current_date):
        return (current_date - self.trade_date).days >= 14
    
    def __str__(self):
        return (f"TradeState(symbol={self.symbol}, quantity={self.quantity}, price={self.price}, "
                f"risk={self.risk}, status={self.order_status}, date={self.trade_date})")

def calculate_current_risk(open_trades, portfolio_size):
    total_risk = 0.0
    for trade in open_trades:
        current_price = float(global_account_data['positions'][trade.symbol]['price'])  
        atr = calculate_atr(fetch_historical_data(trade.symbol))
        risk_per_share = 2 * atr
        position_risk = trade.quantity * risk_per_share
        risk_percent = (position_risk / portfolio_size) * 100
        total_risk += risk_percent
    return total_risk

def get_open_trades(open_positions):
    openTrades = []
    for position in open_positions:
        symbol = position.get('symbol', 'N/A')  # Assuming 'symbol' is the key for the stock symbol
        quantity = float(position.get('quantity', 0))
        price = float(position.get('price', 0))
        position_id = position.get('id', 'N/A')  # Using 'N/A' as a fallback if there's no ID
        side = "buy"  # Assuming all open positions are buys; adjust if needed
        position_status = "open"  # Set a default status if needed

        trade = TradeState(symbol, quantity, price, position_id, side, position_status)
        openTrades.append(trade)
    return openTrades


def check_position_status(position_id):  # Renamed from check_order_status
    position_info = r.account.get_stock_position_info(position_id)  # Adjusted method call
    return position_info['state']

def close_expired_trades(open_trades, portfolio_size):
    current_date = datetime.now()
    for trade in open_trades:
        if trade.is_expired(current_date):
            print(f"Closing expired trade: {trade.symbol}")
            close_trade(trade)

def close_trade(trade):
    r.orders.order_sell_market(trade.symbol, trade.quantity)
    print(f"Trade {trade.symbol} closed.")