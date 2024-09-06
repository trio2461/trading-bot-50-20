# utils/trade_state.py
import robin_stocks.robinhood as r
from datetime import datetime
from utils.analysis import calculate_atr
from utils.api import fetch_historical_data
from utils.account_data import global_account_data


class TradeState:
    def __init__(self, symbol, quantity, purchase_price, atr_percent, stop_loss, stop_limit, order_id, side="buy", order_status="pending"):
        self.symbol = symbol  # Stock symbol
        self.quantity = quantity  # Number of shares
        self.purchase_price = purchase_price  # Purchase price at the time of trade
        self.atr_percent = atr_percent  # ATR percentage at the time of purchase
        self.stop_loss = stop_loss  # Stop loss price
        self.stop_limit = stop_limit  # Stop limit price
        self.order_id = order_id  # Order ID
        self.side = side  # Buy or sell
        self.order_status = order_status  # Status of the trade
        self.trade_date = datetime.now()  # Trade date
        self.risk = self.calculate_risk()  # Calculated risk

    def calculate_risk(self):
        # Calculate the risk in dollar terms, based on the stop loss and purchase price
        risk_per_share = self.purchase_price - self.stop_loss
        total_risk = self.quantity * risk_per_share
        return total_risk

    def is_expired(self, current_date):
        # Define an expiration rule if needed
        return (current_date - self.trade_date).days >= 14  # Example: Trade expires after 14 days

    def __str__(self):
        return (f"TradeState(symbol={self.symbol}, quantity={self.quantity}, purchase_price={self.purchase_price}, "
                f"stop_loss={self.stop_loss}, stop_limit={self.stop_limit}, "
                f"risk={self.risk}, status={self.order_status}, date={self.trade_date})")

 
def calculate_current_risk(open_trades, portfolio_size):
    total_risk_percent = 0.0
    total_risk_dollar = 0.0
    
    for trade in open_trades:
        current_price = float(global_account_data['positions'][trade.symbol]['price'])
        atr = calculate_atr(fetch_historical_data(trade.symbol))
        risk_per_share = 2 * atr
        position_risk_dollar = trade.quantity * risk_per_share
        position_risk_percent = (position_risk_dollar / portfolio_size) * 100
        
        total_risk_percent += position_risk_percent
        total_risk_dollar += position_risk_dollar

    return total_risk_percent, total_risk_dollar  # Return both percent and dollar risk


def get_open_trades(positions):
    open_trades = []
    for symbol, data in positions.items():  # Iterate over the items in positions
        quantity = float(data.get('quantity', 0))
        purchase_price = float(data.get('average_buy_price', 0))
        historical_data = fetch_historical_data(symbol)
        atr = calculate_atr(historical_data)
        atr_percent = (atr / purchase_price) * 100
        stop_loss = purchase_price - (2 * atr)
        stop_limit = purchase_price + (2 * atr)
        trade = TradeState(
            symbol=symbol,  # Use the symbol from the key
            quantity=quantity,
            purchase_price=purchase_price,
            atr_percent=atr_percent,
            stop_loss=stop_loss,
            stop_limit=stop_limit,
            order_id=data.get('id', 'N/A'),
            side="buy",
            order_status="open"
        )
        open_trades.append(trade)
    return open_trades


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