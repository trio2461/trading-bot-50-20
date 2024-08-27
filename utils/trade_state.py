# utils/trade_state.py
import robin_stocks.robinhood as r



class TradeState:
    def __init__(self, symbol, quantity, price, order_id, side):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.order_id = order_id
        self.side = side  # 'buy' or 'sell'
        self.risk = self.calculate_risk()

    def calculate_risk(self):
        # Risk is simply the quantity, as each represents 2% of the portfolio
        return self.quantity

    def __str__(self):
        return f"TradeState(symbol={self.symbol}, quantity={self.quantity}, price={self.price}, risk={self.risk})"

def fetch_open_orders():
    open_orders = r.orders.get_all_open_stock_orders()
    return open_orders

def calculate_current_risk(open_orders):
    total_risk = 0.0
    
    for order in open_orders:
        quantity = float(order['quantity'])
        total_risk += quantity  # Risk is simply the quantity
    
    return total_risk

def get_open_trades(open_orders):
    openTrades = []

    for order in open_orders:
        symbol = order['instrument']['symbol']
        quantity = float(order['quantity'])
        price = float(order['price'])
        order_id = order['id']
        side = order['side']

        trade = TradeState(symbol, quantity, price, order_id, side)
        openTrades.append(trade)
    
    return openTrades