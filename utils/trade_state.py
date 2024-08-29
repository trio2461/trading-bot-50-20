# utils/trade_state.py
import robin_stocks.robinhood as r

class TradeState:
    def __init__(self, symbol, quantity, price, order_id, side, order_status="pending"):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price
        self.order_id = order_id
        self.side = side  # 'buy' or 'sell'
        self.order_status = order_status  # Track the status of the order
        self.risk = self.calculate_risk()

    def calculate_risk(self):
        # Risk is calculated as the quantity for simplicity
        return self.quantity

    def __str__(self):
        return (f"TradeState(symbol={self.symbol}, quantity={self.quantity}, price={self.price}, "
                f"risk={self.risk}, status={self.order_status})")

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
        order_status = check_order_status(order_id)

        trade = TradeState(symbol, quantity, price, order_id, side, order_status)
        openTrades.append(trade)
    
    return openTrades

def check_order_status(order_id):
    # This function checks the status of an order by its ID
    order_info = r.orders.get_stock_order_info(order_id)
    return order_info['state']  # Returns the status of the order (e.g., 'filled', 'cancelled', 'queued')


# # utils/trade_state.py
# import robin_stocks.robinhood as r

# class TradeState:
#     def __init__(self, symbol, quantity, price, order_id, side):
#         self.symbol = symbol
#         self.quantity = quantity
#         self.price = price
#         self.order_id = order_id
#         self.side = side  # 'buy' or 'sell'
#         self.risk = self.calculate_risk()

#     def calculate_risk(self):
#         # Risk is simply the quantity, as each represents 2% of the portfolio
#         return self.quantity

#     def __str__(self):
#         return f"TradeState(symbol={self.symbol}, quantity={self.quantity}, price={self.price}, risk={self.risk})"

# def fetch_open_orders():
#     open_orders = r.orders.get_all_open_stock_orders()
#     return open_orders

# def calculate_current_risk(open_orders):
#     total_risk = 0.0
    
#     for order in open_orders:
#         quantity = float(order['quantity'])
#         total_risk += quantity  # Risk is simply the quantity
    
#     return total_risk

# def get_open_trades(open_orders):
#     openTrades = []

#     for order in open_orders:
#         symbol = order['instrument']['symbol']
#         quantity = float(order['quantity'])
#         price = float(order['price'])
#         order_id = order['id']
#         side = order['side']

#         trade = TradeState(symbol, quantity, price, order_id, side)
#         openTrades.append(trade)
    
#     return openTrades

# This code defines a TradeState class that represents a trade with the symbol, quantity, price, order ID, and side (buy or sell). The calculate_risk method calculates the risk of the trade based on the quantity. The fetch_open_orders function retrieves all open stock orders from Robinhood, the calculate_current_risk function calculates the total risk of all open orders, and the get_open_trades function creates TradeState objects for each open trade. These functions are used to manage the state of trades in the trading bot.