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
def get_open_positions():  
    open_positions = r.account.get_open_stock_positions()
    print("Open Positions:")
    print(open_positions)
if __name__ == "__main__":
    login_to_robinhood()
    get_open_positions()

# bot.py
from utils.api import get_top_movers, load_csv_data, sanitize_ticker_symbols
from utils.account_data import global_account_data, update_global_account_data
from utils.trading import analyze_stock, send_trade_summary, execute_trade, check_and_execute_sells
from utils.trade_state import calculate_current_risk, get_open_trades  
from utils.settings import SIMULATED, SIMULATED_PORTFOLIO_SIZE, MAX_DAILY_LOSS, USE_CSV_DATA, USE_NASDAQ_DATA, USE_SP500_DATA, ATR_THRESHOLDS
from termcolor import colored
import robin_stocks.robinhood as r
def main():
    update_global_account_data()
    simulated = SIMULATED  
    if simulated:
        portfolio_size = SIMULATED_PORTFOLIO_SIZE  
    else:
        portfolio_size = float(global_account_data['portfolio_info']['equity'])  
    max_daily_loss = portfolio_size * MAX_DAILY_LOSS
    open_positions = r.account.get_open_stock_positions()  
    open_trades = get_open_trades(open_positions)  
    current_risk = calculate_current_risk(open_trades, portfolio_size)
    risk_available_for_new_trades = max_daily_loss - current_risk
    stock_symbols = []
    if USE_CSV_DATA:
        if USE_NASDAQ_DATA and not USE_SP500_DATA:
            nasdaq_data = load_csv_data('nasdaq100_full.csv', 'nasdaq')
            nasdaq_data = sanitize_ticker_symbols(nasdaq_data)
            stock_symbols = nasdaq_data['Ticker'].tolist()
        elif USE_SP500_DATA and not USE_NASDAQ_DATA:
            sp500_data = load_csv_data('sp500_companies.csv', 'sp500')
            sp500_data = sanitize_ticker_symbols(sp500_data)
            stock_symbols = sp500_data['Symbol'].tolist()
        elif USE_NASDAQ_DATA and USE_SP500_DATA:
            nasdaq_data = load_csv_data('nasdaq100_full.csv', 'nasdaq')
            nasdaq_data = sanitize_ticker_symbols(nasdaq_data)
            sp500_data = load_csv_data('sp500_companies.csv', 'sp500')
            sp500_data = sanitize_ticker_symbols(sp500_data)
            stock_symbols = nasdaq_data['Ticker'].tolist() + sp500_data['Symbol'].tolist()
    else:
        stock_symbols = get_top_movers()
    results = []
    total_stocks_analyzed = 0
    total_trades_made = 0
    for stock in stock_symbols:
        print(f"\n--- Analyzing {stock} ---")
        eligible_for_trade = analyze_stock(stock, results, portfolio_size, current_risk, atr_thresholds=ATR_THRESHOLDS, simulated=simulated)
        total_stocks_analyzed += 1
    print(colored(f"\nInitial Risk (from open positions): {current_risk:.2f}% of Portfolio", 'yellow'))
    print(colored(f"Max Allowed Risk: {MAX_DAILY_LOSS * 100:.2f}% of Portfolio", 'yellow'))
    print(colored(f"Risk Available for New Trades: ${risk_available_for_new_trades:.2f}", 'yellow'))
    print(colored("\n--- Analysis Summary ---", 'yellow'))
    for result in results:
        print(f"{result['Stock']}: {colored('Eligible for Trade:', 'blue')} {result['Eligible for Trade']}, "
            f"ATR Percent: {colored(f'{result['ATR Percent']:.2f}%', 'cyan')}, "
            f"Reason: {result['Reason']}")
    results.sort(key=lambda x: x['ATR Percent'], reverse=True)
    top_trades = [trade for trade in results if trade['Eligible for Trade']][:3]
    for trade in top_trades:
        if current_risk >= max_daily_loss:
            print(colored(f"Daily loss limit exceeded. No more trades will be made.", 'red'))
            break
        elif trade['Risk Dollar'] > risk_available_for_new_trades:
            print(colored(f"Trade for {trade['Stock']} skipped due to insufficient risk allowance.", 'red'))
            continue
        trade_made = execute_trade(trade, portfolio_size, current_risk, simulated)
        if trade_made:
            total_trades_made += 1
            current_risk += trade['Risk Dollar']  
            risk_available_for_new_trades -= trade['Risk Dollar']  
            print(f"Updated Risk after trade: {current_risk:.2f}% of Portfolio")  
            print(f"Risk Available for New Trades: ${risk_available_for_new_trades:.2f}")
            print(f"Portfolio size after trade: ${portfolio_size:.2f}")  
        print("\n")
    print(colored(f"\n--- Final Portfolio Size at the End: ${portfolio_size:.2f} ---", 'cyan'))
    print("\n--- Current Positions ---\n")
    positions = global_account_data['positions']
    if positions:
        for symbol, data in positions.items():
            print(f"\nStock: {data['name']}")
            print(f" - Quantity: {data['quantity']} shares")
            print(f" - Current Price: ${data['price']}")
            print(f" - Average Buy Price: ${data['average_buy_price']}")
            print(f" - Equity: ${data['equity']}")
            print(f" - Percent Change: {data['percent_change']}%")
            print(f" - Equity Change: ${data['equity_change']}\n")
    else:
        print("No positions found.")
    send_trade_summary(top_trades, portfolio_size, current_risk, open_trades)
    print(colored("\n--- Summary of Top Three Bullish Crossover Trades ---", 'yellow'))
    for result in top_trades:
        print(f"{result['Stock']}: {colored('Eligible for Trade:', 'blue')} {result['Eligible for Trade']}, {colored('Trade Made:', 'blue')} {result['Trade Made']}, Trade Amount: ${result['Trade Amount']:.2f}, Shares to Purchase: {result['Shares to Purchase']:.2f} shares, Potential Gain: ${result['Potential Gain']:.2f}, Risk: {result['Risk Percent']:.2f}% (${result['Risk Dollar']:.2f}), ATR: {result['ATR']:.2f} ({result['ATR Percent']:.2f}%), ATR * 2: {result['ATR * 2']:.2f}%, Reason: {result['Reason']}")
    print(colored(f"\n--- Portfolio Size at the End: ${portfolio_size} ---", 'cyan'))
    print(colored(f"\n--- Total Number of Stocks Analyzed: {total_stocks_analyzed} ---", 'cyan'))
    print(colored(f"\n--- Total Possible Number of Trades Made: {total_trades_made} ---", 'cyan'))
    print(colored("\n--- All Possible Trades ---", 'green'))
    for idx, trade in enumerate(results, start=1):
        print(f"{idx}. Stock: {colored(trade['Stock'], 'yellow')}, ATR Percent: {colored(f'{trade['ATR Percent']:.2f}%', 'cyan')}, "
            f"Eligible: {colored(trade['Eligible for Trade'], 'blue')}, Trade Amount: {colored(f'${trade['Trade Amount']:.2f}', 'magenta')}, "
            f"Risk Percent: {colored(f'{trade['Risk Percent']:.2f}%', 'red')}")
    print(colored("\n--- Top Three Trades ---", 'yellow'))
    for idx, trade in enumerate(top_trades, start=1):
        print(f"{idx}. Stock: {colored(trade['Stock'], 'yellow')}, ATR Percent: {colored(f'{trade['ATR Percent']:.2f}%', 'cyan')}, "
            f"Eligible: {colored(trade['Eligible for Trade'], 'blue')}, Trade Amount: {colored(f'${trade['Trade Amount']:.2f}', 'magenta')}, "
            f"Risk Percent: {colored(f'{trade['Risk Percent']:.2f}%', 'red')}")
if __name__ == "__main__":
    main()

# gpt.py
import os
import re
output_file = "combined_minified.py"
ignore_dirs = {"__pycache__", "env"}
ignore_files = {"__init__.py", output_file}
def minify_python_code(code):
    code = re.sub(r'
    code = os.linesep.join([s for s in code.splitlines() if s.strip()])
    return code
def combine_files(root_dir):
    with open(output_file, 'w') as outfile:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
            for filename in filenames:
                if filename.endswith('.py') and filename not in ignore_files:
                    file_path = os.path.join(dirpath, filename)
                    with open(file_path, 'r') as infile:
                        code = infile.read()
                        minified_code = minify_python_code(code)
                        outfile.write(f"
                        outfile.write(minified_code + "\n\n")
if __name__ == "__main__":
    combine_files(".")

# close_all_positions.py
import robin_stocks.robinhood as r
from dotenv import load_dotenv  
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
        order = r.orders.order(
            symbol=symbol,
            quantity=quantity,
            side='sell',
            timeInForce='gfd',  
            market_hours='regular_hours'  
        )
        print(f"Response from Robinhood: {order}")
        if 'id' in order:
            print(f"Position for {symbol} closed successfully.")
        else:
            print(f"Failed to close position for {symbol}. Response: {order}")
if __name__ == "__main__":
    login_to_robinhood()
    close_all_positions()

# setup_cron.py
import os
import subprocess
import sys
current_directory = os.path.dirname(os.path.abspath(__file__))
python_path = os.path.join(current_directory, "env/bin/python")
script_path = os.path.join(current_directory, "bot.py")
log_path = os.path.join(current_directory, "error_log.txt")
cron_command = f"30 9-16 * * 1-5 {python_path} {script_path} >> {log_path} 2>&1"
def setup_cron_job():
    result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    current_crontab = result.stdout
    if cron_command not in current_crontab:
        with open('my_crontab', 'w') as f:
            if current_crontab:
                f.write(current_crontab)
            f.write(cron_command + '\n')
        subprocess.run(['crontab', 'my_crontab'])
        os.remove('my_crontab')
        print("Cron job added successfully.")
    else:
        print("Cron job already exists.")
def remove_cron_job():
    result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    current_crontab = result.stdout
    if cron_command in current_crontab:
        new_crontab = current_crontab.replace(cron_command + '\n', '')
        with open('my_crontab', 'w') as f:
            f.write(new_crontab)
        subprocess.run(['crontab', 'my_crontab'])
        os.remove('my_crontab')
        print("Cron job removed successfully.")
    else:
        print("Cron job does not exist.")
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--remove':
        remove_cron_job()
    else:
        setup_cron_job()

# analysis.py
def moving_average(data, period):
    return [sum(data[i:i+period])/period for i in range(len(data)-period+1)]
def calculate_atr(historicals, period=14):
    tr_list = []
    for i in range(1, len(historicals)):
        high_low = float(historicals[i]['high_price']) - float(historicals[i]['low_price'])
        high_close = abs(float(historicals[i]['high_price']) - float(historicals[i-1]['close_price']))
        low_close = abs(float(historicals[i]['low_price']) - float(historicals[i-1]['close_price']))
        true_range = max(high_low, high_close, low_close)
        tr_list.append(true_range)
    initial_atr = sum(tr_list[:period]) / period
    atr_values = [initial_atr]
    for i in range(period, len(tr_list)):
        current_atr = (atr_values[-1] * (period - 1) + tr_list[i]) / period
        atr_values.append(current_atr)
    return atr_values[-1]
def detect_recent_crossover(ma_short, ma_long, days=5):
    if len(ma_short) < days + 1 or len(ma_long) < days + 1:
        return None
    for i in range(1, days + 1):
        if ma_short[-i-1] <= ma_long[-i-1] and ma_short[-i] > ma_long[-i]:
            return "Bullish Crossover"
    return None
def check_recent_crossovers(stock, ma_short, ma_long):
    if len(ma_short) < 5 or len(ma_long) < 5:
        return True  
    for i in range(1, 5):
        if detect_recent_crossover(ma_short[-i:], ma_long[-i:]) == "Bearish Crossover":
            return False
    return True

# send_message.py
from utils.settings import PHONE_NUMBER
import subprocess
def send_text_message(message, phone_number=PHONE_NUMBER):
    applescript_command = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "{phone_number}" of targetService
        send "{message}" to targetBuddy
    end tell
    '''
    subprocess.run(['osascript', '-e', applescript_command])

# trade_state.py
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
        symbol = position.get('symbol', 'N/A')  
        quantity = float(position.get('quantity', 0))
        price = float(position.get('price', 0))
        position_id = position.get('id', 'N/A')  
        side = "buy"  
        position_status = "open"  
        trade = TradeState(symbol, quantity, price, position_id, side, position_status)
        openTrades.append(trade)
    return openTrades
def check_position_status(position_id):  
    position_info = r.account.get_stock_position_info(position_id)  
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

# account_data.py
import robin_stocks.robinhood as r
import os
from dotenv import load_dotenv
load_dotenv()
global_account_data = {}
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
    print("Account Info:")
    print(global_account_data['account_info'])
    print("\nPortfolio Info:")
    print(global_account_data['portfolio_info'])
    print("\nPositions:")
    print(global_account_data['positions'])
login_to_robinhood()
update_global_account_data()
test_print_global_account_data()

# trading.py
from utils.analysis import moving_average, calculate_atr, detect_recent_crossover, check_recent_crossovers
from utils.api import fetch_historical_data, order_buy_market, get_positions
from utils.settings import SIMULATED, MAX_DAILY_LOSS, ATR_THRESHOLDS, PHONE_NUMBER
from utils.send_message import send_text_message
from utils.trade_state import TradeState,calculate_current_risk, get_open_trades
from termcolor import colored  
def is_market_open():
    from datetime import datetime, time
    now = datetime.now().time()
    market_open = time(9, 30)
    market_close = time(16, 0)
    return market_open <= now <= market_close
def analyze_stock(stock, results, portfolio_size, current_risk, simulated=SIMULATED, atr_thresholds=ATR_THRESHOLDS):
    print(f"\n--- Analyzing {stock} ---")
    historicals = fetch_historical_data(stock)
    if not historicals or len(historicals) < 50:  
        print(f"Not enough data for {stock}. Skipping...")
        return False
    closing_prices = [float(day['close_price']) for day in historicals]
    ma_20 = moving_average(closing_prices, 20)
    ma_50 = moving_average(closing_prices, 50)
    crossover_signal = detect_recent_crossover(ma_20[-len(ma_50):], ma_50, days=5)
    atr = calculate_atr(historicals)
    atr_percent = (atr / closing_prices[-1]) * 100 if closing_prices[-1] != 0 else 0
    share_price = closing_prices[-1]  
    if atr_percent < 3.0:
        print(f"{stock} skipped due to ATR percent being less than 3% ({atr_percent:.2f}%).")
        return False
    if atr_percent < 3.5:
        classified_atr_percent = 3.0
    elif atr_percent < 4.5:
        classified_atr_percent = 4.0
    else:
        classified_atr_percent = 5.0
    if crossover_signal == "Bullish Crossover" and classified_atr_percent in atr_thresholds:
        print(f"Eligible Bullish Crossover found for {stock} with Classified ATR: {classified_atr_percent}%")
        two_atr = 2 * (classified_atr_percent / 100)
        purchase_amount = (0.02 * portfolio_size) / two_atr
        shares_to_purchase = purchase_amount / share_price  
        potential_loss = purchase_amount * two_atr
        potential_gain = potential_loss  
        risk_percent = (potential_loss / portfolio_size) * 100  
        if potential_loss <= portfolio_size * 0.02 and current_risk + potential_loss <= MAX_DAILY_LOSS * portfolio_size:
            results.append({
                'Stock': stock,
                'ATR': atr,
                'ATR Percent': atr_percent,
                'ATR * 2': two_atr * 100,  
                'Share Price': share_price,
                'Eligible for Trade': True,
                'Trade Made': False,  
                'Order Status': "Not Attempted",  
                'Order ID': None,
                'Trade Amount': purchase_amount,
                'Shares to Purchase': shares_to_purchase,
                'Potential Gain': potential_gain,
                'Risk Percent': risk_percent,
                'Risk Dollar': potential_loss,
                'Reason': "Criteria met"
            })
            current_risk += potential_loss  
            print(f"Adding eligible trade for {stock}.")
        else:
            print(f"Skipping {stock} due to risk exceeding limits.")
    else:
        if crossover_signal == "Bullish Crossover":
            print(f"{stock} had a Bullish Crossover but was not eligible due to ATR or risk criteria.\n")
    return True  
def execute_trade(trade, portfolio_size, current_risk, simulated):
    positions = get_positions()
    if trade['Stock'] in positions:
        print(f"\nTrade for {trade['Stock']} skipped because it's already in the portfolio.")
        return False
    new_risk_percent = (trade['Risk Dollar'] / portfolio_size) * 100
    total_risk_after_trade = current_risk + new_risk_percent
    if total_risk_after_trade > (MAX_DAILY_LOSS * 100):
        print(f"Trade for {trade['Stock']} skipped due to exceeding max risk limits.")
        return False
    print(f'\nExecuting trade for: {trade["Stock"]}, Simulated={simulated}\n')
    if is_market_open() and not simulated:
        order_result = order_buy_market(trade['Stock'], int(trade['Shares to Purchase']))
        if isinstance(order_result, dict):
            order_id = order_result.get('id')
            if order_id:
                order_status = check_order_status(order_id)
                if order_status == 'filled':
                    trade['Trade Made'] = True
                    trade['Order Status'] = order_status
                    trade['Order ID'] = order_id
                    current_risk += new_risk_percent  
                    print(f"Trade executed for {trade['Stock']}. Order ID: {order_id}")
                    return True
                else:
                    print(f"Trade for {trade['Stock']} was not filled. Order status: {order_status}")
                    return False
            else:
                print(f"Order for {trade['Stock']} failed to create properly.")
                return False
        else:
            print(f"Trade for {trade['Stock']} failed to execute. Response: {order_result}")
            return False
    else:
        print(f"Simulated or out-of-hours trade for {trade['Stock']}.")
        trade['Trade Made'] = True
        trade['Order Status'] = "Simulated"
        trade['Order ID'] = "SIM12345"
        current_risk += new_risk_percent
        return True
def check_and_execute_sells(open_trades, portfolio_size):
    for trade in open_trades:
        current_price = float(r.stocks.get_latest_price(trade.symbol)[0])
        target_sell_price = trade.price + (trade.price * trade.risk / trade.quantity)  
        if current_price >= target_sell_price:
            print(f"Selling {trade.quantity} shares of {trade.symbol} at {current_price}")
            order_result = r.orders.order_sell_market(trade.symbol, trade.quantity)
            if isinstance(order_result, dict):  
                order_id = order_result.get('id')
                if order_id:
                    print(f"Sold {trade.symbol} successfully. Order ID: {order_id}")
                else:
                    print(f"Sell order for {trade.symbol} failed to create properly.")
            else:
                print(f"Failed to sell {trade.symbol}. Response: {order_result}")
def send_trade_summary(top_trades, portfolio_size, current_risk, open_trades, simulated=SIMULATED):
    summary_message = "\n--- Trade Summary ---\n"
    mode = "SIMULATED" if simulated else "LIVE"
    summary_message += f"Mode: {mode}\n\n"
    for trade in top_trades:
        summary_message += f"Stock: {trade['Stock']}\n"
        summary_message += f"Trade Made: {trade['Trade Made']}\n"
        summary_message += f"Trade Amount: ${trade['Trade Amount']:.2f}\n"
        summary_message += f"Shares to Purchase: {trade['Shares to Purchase']:.2f} shares\n"
        summary_message += f"Potential Gain: ${trade['Potential Gain']:.2f}\n"
        summary_message += f"Risk Percent: {trade['Risk Percent']:.2f}%\n"
        summary_message += f"Risk Dollar: ${trade['Risk Dollar']:.2f}\n"
        summary_message += f"ATR: {trade['ATR']:.2f}%\n"
        summary_message += "\n"  
    summary_message += f"\nPortfolio Size: ${portfolio_size:.2f}\n"
    summary_message += f"Current Risk: ${current_risk:.2f}\n"
    summary_message += "\n--- Open Trades ---\n"
    for trade in open_trades:
        summary_message += f"Symbol: {trade.symbol}\n"
        summary_message += f"Quantity: {trade.quantity}\n"
        summary_message += f"Price: ${trade.price:.2f}\n"
        summary_message += f"Risk: {trade.risk}\n"
        summary_message += f"Side: {trade.side.capitalize()}\n"
        summary_message += "\n"  
    send_text_message(summary_message, phone_number=PHONE_NUMBER)

# api.py
import robin_stocks.robinhood as r
import os
import logging
import contextlib
import pandas as pd
from dotenv import load_dotenv  
from utils.settings import SIMULATED, SIMULATED_PORTFOLIO_SIZE  
load_dotenv()
def login_to_robinhood():
    username = os.getenv('ROBINHOOD_USERNAME')
    password = os.getenv('ROBINHOOD_PASSWORD')
    r.login(username=username, password=password)
def get_positions():
    positions = r.account.build_holdings()
    print(f"Current Positions: {positions}")
    return positions
def order_buy_market(symbol, quantity):
    try:
        order = r.orders.order_buy_market(symbol, quantity)
        order_id = order.get('id')  
        return order_id
    except Exception as e:
        print(f"Error placing market order: {e}")
        return None
def fetch_historical_data(stock, interval='day', span='3month'):
    try:
        sanitized_stock = stock.replace('-', '')
        with contextlib.redirect_stdout(None):  
            data = r.stocks.get_stock_historicals(sanitized_stock, interval=interval, span=span)
        return data
    except (r.exceptions.APIError, r.exceptions.RequestError, r.exceptions.NotFound) as e:
        logging.error(f"Failed to fetch data for {stock}: {e}")
        return None
def get_top_movers(direction='up'):
    try:
        movers = r.markets.get_top_movers_sp500(direction=direction)
        symbols = [mover['symbol'] for mover in movers]
        return symbols
    except Exception as e:
        logging.error(f"Failed to fetch top movers: {e}")
        return []
def get_portfolio_size(simulated=SIMULATED, simulated_size=SIMULATED_PORTFOLIO_SIZE):  
    if simulated:
        return simulated_size
    else:
        portfolio = r.profiles.load_account_profile(info='portfolio_cash')
        return float(portfolio)
def load_csv_data(file_path, exchange):
    df = pd.read_csv(file_path)
    if exchange.lower() == 'nasdaq':
        return df[['Ticker']]  
    elif exchange.lower() == 'sp500':
        return df[['Symbol']]  
    else:
        raise ValueError("Unsupported exchange. Please use 'nasdaq' or 'sp500'.")
def sanitize_ticker_symbols(df):
    """
    Sanitizes ticker symbols in the DataFrame.
    :param df: DataFrame containing the data.
    :return: DataFrame with sanitized ticker symbols.
    """
    column_name = df.columns[0]  
    df[column_name] = df[column_name].str.replace('-', '', regex=True)  
    df[column_name] = df[column_name].str.strip()  
    df[column_name] = df[column_name].str.upper()  
    return df

# settings.py
SIMULATED = False  
SIMULATED_PORTFOLIO_SIZE = 20000  
MAX_DAILY_LOSS = 0.06  
PHONE_NUMBER = '252-571-5303'
USE_CSV_DATA = True  
USE_NASDAQ_DATA = False  
USE_SP500_DATA = True  
ATR_THRESHOLDS = (3.0, 4.0, 5.0)  

