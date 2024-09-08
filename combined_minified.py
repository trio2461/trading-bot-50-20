# quick_test.py
from dotenv import load_dotenv
import os
import robin_stocks.robinhood as r
from utils.account_data import global_account_data, update_global_account_data
from datetime import datetime
load_dotenv()
def login_to_robinhood():
    username = os.getenv('ROBINHOOD_USERNAME')
    password = os.getenv('ROBINHOOD_PASSWORD')
    if not username or not password:
        raise Exception("ROBINHOOD_USERNAME or ROBINHOOD_PASSWORD not found in the environment variables.")
    r.login(username=username, password=password)
def get_open_position_symbols():
    positions = global_account_data.get('positions', {})
    open_position_symbols = [symbol for symbol in positions]
    print("Open Position Symbols:")
    print(open_position_symbols)
    return open_position_symbols
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
                    matched_orders[stock_symbol] = created_at  
            else:
                print("No instrument URL found in order.")
    else:
        print("No stock orders found.")
    return matched_orders
def update_global_account_data_with_dates(matched_symbols_dict):
    positions = global_account_data.get('positions', {})
    for symbol, created_at in matched_symbols_dict.items():
        if symbol in positions:
            positions[symbol]['created_at'] = created_at
    global_account_data['positions'] = positions  
if __name__ == "__main__":
    login_to_robinhood()
    update_global_account_data()  
    open_position_symbols = get_open_position_symbols()
    matched_symbols_dict = get_stock_orders_and_match_open_positions(open_position_symbols)
    update_global_account_data_with_dates(matched_symbols_dict)
    print("\nUpdated Global Account Data:")
    import json
    print(json.dumps(global_account_data, indent=4))

# data_loader.py
from utils.api import sanitize_ticker_symbols
import pandas as pd
from utils.settings import USE_CSV_DATA, USE_NASDAQ_DATA, USE_SP500_DATA  
def load_stock_symbols():
    stock_symbols = []
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
    return stock_symbols
def load_csv_data(file_path, exchange):
    df = pd.read_csv(file_path)
    if exchange.lower() == 'nasdaq':
        return df[['Ticker']]  
    elif exchange.lower() == 'sp500':
        return df[['Symbol']]  
    else:
        raise ValueError("Unsupported exchange. Please use 'nasdaq' or 'sp500'.")

# logger.py
from termcolor import colored
from datetime import datetime
import json  
def log_initial_risk(current_risk_percent, max_allowed_risk, risk_available_for_new_trades):
    print(colored(f"\nInitial Risk (from open positions): {current_risk_percent:.2f}% of Portfolio", 'yellow'))
    print(colored(f"Max Allowed Risk: {max_allowed_risk:.2f}% of Portfolio", 'yellow'))
    print(colored(f"Risk Available for New Trades: ${risk_available_for_new_trades:.2f}", 'yellow'))
def log_analysis_summary(results):
    print(colored("\n--- Analysis Summary ---", 'yellow'))
    for result in results:
        print(f"{result['Stock']}: {colored('Eligible for Trade:', 'blue')} {result['Eligible for Trade']}, "
              f"ATR Percent: {colored(f'{result['ATR Percent']:.2f}%', 'cyan')}, "
              f"Reason: {result['Reason']}")
def log_trade_execution_skipped(stock, reason):
    print(colored(f"Trade for {stock} skipped due to {reason}.", 'red'))
def log_trade_execution_success(stock, current_risk_percent, risk_available_for_new_trades):
    print(f"Updated Risk after trade: {current_risk_percent:.2f}% of Portfolio")
    print(f"Risk Available for New Trades: ${risk_available_for_new_trades:.2f}")
def log_final_portfolio_size(portfolio_size):
    print(colored(f"\n--- Final Portfolio Size at the End: ${portfolio_size:.2f} ---", 'cyan'))
def log_current_positions(positions):
    print("\n--- Current Positions ---\n")
    if positions:
        for symbol, data in positions.items():
            purchase_date_str = data.get('purchase_date') or data.get('created_at', None)
            print(f"Debug: Purchase date for {symbol}: {purchase_date_str}")
            if purchase_date_str:
                try:
                    purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    days_held = (datetime.now() - purchase_date).days
                except ValueError:
                    print(f"Error parsing purchase date for {symbol}, setting days held to 0")
                    days_held = 0
            else:
                print(f"No purchase date or created_at for {symbol}, setting days held to 0")
                days_held = 0
            positions[symbol]['days_held'] = days_held
            created_at = data.get('created_at', 'N/A')
            print(f"Stock: {colored(data['name'], 'yellow')}")
            print(f" - Days Held: {colored(f'{days_held}', 'green')} days")
            print(f" - Created At: {colored(f'{created_at}', 'green')}\n")
    else:
        print("No positions found.")
def log_top_trades(top_trades):
    print(colored("\n--- Summary of Top Three Bullish Crossover Trades ---", 'yellow'))
    for result in top_trades:
        print(f"{result['Stock']}: {colored('Eligible for Trade:', 'blue')} {result['Eligible for Trade']}, {colored('Trade Made:', 'blue')} {result['Trade Made']}, "
              f"Trade Amount: ${result['Trade Amount']:.2f}, Shares to Purchase: {result['Shares to Purchase']:.2f} shares, "
              f"Potential Gain: ${result['Potential Gain']:.2f}, Risk: {result['Risk Percent']:.2f}% (${result['Risk Dollar']:.2f}), "
              f"ATR: {result['ATR']:.2f} ({result['ATR Percent']:.2f}%), ATR * 2: {result['ATR * 2']:.2f}%, Reason: {result['Reason']}")
def log_all_possible_trades(results):
    print(colored("\n--- All Possible Trades ---", 'green'))
    for idx, trade in enumerate(results, start=1):
        print(f"{idx}. Stock: {colored(trade['Stock'], 'yellow')}, ATR Percent: {colored(f'{trade['ATR Percent']:.2f}%', 'cyan')}, "
              f"Eligible: {colored(trade['Eligible for Trade'], 'blue')}, Trade Amount: {colored(f'${trade['Trade Amount']:.2f}', 'magenta')}, "
              f"Risk Percent: {colored(f'{trade['Risk Percent']:.2f}%', 'red')}")
def log_top_three_trades(top_trades):
    print(colored("\n--- Top Three Trades ---", 'yellow'))
    for idx, trade in enumerate(top_trades, start=1):
        print(f"{idx}. Stock: {colored(trade['Stock'], 'yellow')}, ATR Percent: {colored(f'{trade['ATR Percent']:.2f}%', 'cyan')}, "
              f"Eligible: {colored(trade['Eligible for Trade'], 'blue')}, Trade Amount: {colored(f'${trade['Trade Amount']:.2f}', 'magenta')}, "
              f"Risk Percent: {colored(f'{trade['Risk Percent']:.2f}%', 'red')}")

# bot.py
from utils.api import get_top_movers, load_csv_data, sanitize_ticker_symbols, login_to_robinhood
from utils.account_data import global_account_data, update_global_account_data
from utils.trading import analyze_stock, send_trade_summary, execute_trade, check_positions_against_atr, get_stock_orders_and_match_open_positions, close_trades_open_for_ten_days
from utils.trade_state import calculate_current_risk, get_open_trades
from utils.settings import SIMULATED, SIMULATED_PORTFOLIO_SIZE, MAX_DAILY_LOSS, USE_CSV_DATA, ATR_THRESHOLDS  
from data_loader import load_stock_symbols  
import robin_stocks.robinhood as r
from tqdm import tqdm
import logger  
import json
def main():
    login_to_robinhood();
    update_global_account_data()
    close_trades_open_for_ten_days(global_account_data['positions'])
    check_positions_against_atr(global_account_data)
    simulated = SIMULATED  
    portfolio_size = SIMULATED_PORTFOLIO_SIZE if simulated else float(global_account_data['portfolio_info']['equity'])  
    max_daily_loss = portfolio_size * MAX_DAILY_LOSS
    open_position_symbols = [symbol for symbol in global_account_data['positions']]  
    matched_orders = get_stock_orders_and_match_open_positions(open_position_symbols)
    for symbol, created_at in matched_orders.items():
        if symbol in global_account_data['positions']:
            global_account_data['positions'][symbol]['created_at'] = created_at  
    open_trades = get_open_trades(global_account_data['positions'])  
    current_risk_percent, current_risk_dollar = calculate_current_risk(open_trades, portfolio_size)
    risk_available_for_new_trades = max_daily_loss - current_risk_dollar
    if USE_CSV_DATA:
        stock_symbols = load_stock_symbols()  
    else:
        stock_symbols = get_top_movers()
    with tqdm(stock_symbols, desc="Analyzing stocks", position=0, leave=True, ncols=100) as progress_bar:
        results = []
        total_stocks_analyzed = 0
        total_trades_made = 0
        for stock in stock_symbols:
            progress_bar.set_description(f"Analyzing {stock}")
            eligible_for_trade = analyze_stock(stock, results, portfolio_size, current_risk_percent, atr_thresholds=ATR_THRESHOLDS, simulated=simulated)
            total_stocks_analyzed += 1
            progress_bar.update(1)  
            if not eligible_for_trade:
                tqdm.write(f"{stock} skipped due to ATR percent being less than 3%.")
    logger.log_initial_risk(current_risk_percent, MAX_DAILY_LOSS * 100, risk_available_for_new_trades)
    logger.log_analysis_summary(results)
    results.sort(key=lambda x: x['ATR Percent'], reverse=True)
    top_trades = [trade for trade in results if trade['Eligible for Trade']][:3]
    for trade in top_trades:
        if current_risk_percent >= MAX_DAILY_LOSS * 100:
            logger.log_trade_execution_skipped(trade['Stock'], "exceeding daily loss limit")
            break
        elif trade['Risk Dollar'] > risk_available_for_new_trades:
            logger.log_trade_execution_skipped(trade['Stock'], "insufficient risk allowance")
            continue
        trade_made = execute_trade(trade, portfolio_size, current_risk_percent, simulated)
        if trade_made:
            new_risk_percent = (trade['Risk Dollar'] / portfolio_size) * 100
            current_risk_percent += new_risk_percent
            risk_available_for_new_trades -= trade['Risk Dollar']
            logger.log_trade_execution_success(trade['Stock'], current_risk_percent, risk_available_for_new_trades)
    logger.log_final_portfolio_size(portfolio_size)
    logger.log_current_positions(global_account_data['positions'])
    send_trade_summary(top_trades, portfolio_size, current_risk_percent, open_trades, global_account_data)
    logger.log_top_trades(top_trades)
    logger.log_all_possible_trades(results)
    logger.log_top_three_trades(top_trades)
if __name__ == "__main__":
    main()

# bot_schedule.py
import schedule
import logging
import signal
import sys
from bot import main
from datetime import datetime, time as datetime_time
import time
logging.basicConfig(filename='bot_schedule.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
def market_hours():
    now = datetime.now().time()
    market_open = datetime_time(9, 30)
    market_close = datetime_time(16, 0)
    return market_open <= now <= market_close
def run_main():
    try:
        if market_hours():
            logging.info("Running main every minute during market hours...")
            main()
        else:
            logging.info("Running main every 5 hours during non-market hours...")
    except Exception as e:
        logging.error(f"Error occurred during run_main: {e}")
def signal_handler(sig, frame):
    logging.info("Received termination signal. Shutting down...")
    logging.info("Scheduler stopped at: %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
logging.info("Scheduler started at: %s", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
schedule.every(1).minute.do(lambda: run_main() if market_hours() else None)
schedule.every(5).hours.do(lambda: run_main() if not market_hours() else None)
logging.info("Scheduler running...")
while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        logging.error(f"Error in the scheduler loop: {e}")

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
    def __init__(self, symbol, quantity, purchase_price, atr_percent, stop_loss, stop_limit, order_id, side="buy", order_status="pending"):
        self.symbol = symbol  
        self.quantity = quantity  
        self.purchase_price = purchase_price  
        self.atr_percent = atr_percent  
        self.stop_loss = stop_loss  
        self.stop_limit = stop_limit  
        self.order_id = order_id  
        self.side = side  
        self.order_status = order_status  
        self.trade_date = datetime.now()  
        self.risk = self.calculate_risk()  
    def calculate_risk(self):
        risk_per_share = self.purchase_price - self.stop_loss
        total_risk = self.quantity * risk_per_share
        return total_risk
    def is_expired(self, current_date):
        return (current_date - self.trade_date).days >= 14  
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
    return total_risk_percent, total_risk_dollar  
def get_open_trades(positions):
    open_trades = []
    for symbol, data in positions.items():  
        quantity = float(data.get('quantity', 0))
        purchase_price = float(data.get('average_buy_price', 0))
        historical_data = fetch_historical_data(symbol)
        atr = calculate_atr(historical_data)
        atr_percent = (atr / purchase_price) * 100
        stop_loss = purchase_price - (2 * atr)
        stop_limit = purchase_price + (2 * atr)
        trade = TradeState(
            symbol=symbol,  
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
global_account_data = {
    'risk_percent': 0.0,  
    'risk_dollar': 0.0    
}
def update_risk_in_global_data(new_risk_percent, new_risk_dollar):
    global_account_data['risk_percent'] += new_risk_percent
    global_account_data['risk_dollar'] += new_risk_dollar
def reset_risk_in_global_data():
    global_account_data['risk_percent'] = 0.0
    global_account_data['risk_dollar'] = 0.0
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

# trading.py
import robin_stocks.robinhood as r
from utils.analysis import moving_average, calculate_atr, detect_recent_crossover, check_recent_crossovers
from utils.api import fetch_historical_data, order_buy_market
from utils.settings import SIMULATED, MAX_DAILY_LOSS, ATR_THRESHOLDS, PHONE_NUMBER
from utils.send_message import send_text_message
from utils.trade_state import TradeState,calculate_current_risk, get_open_trades
from termcolor import colored
from datetime import datetime, timedelta
def is_market_open():
    from datetime import datetime, time
    now = datetime.now().time()
    market_open = time(9, 30)
    market_close = time(16, 0)
    return market_open <= now <= market_close
def analyze_stock(stock, results, portfolio_size, current_risk, simulated=SIMULATED, atr_thresholds=ATR_THRESHOLDS):
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
def execute_trade(trade, portfolio_size, current_risk_percent, simulated):
    positions = global_account_data['positions']  
    if trade['Stock'] in positions:
        print(f"\nTrade for {trade['Stock']} skipped because it's already in the portfolio.")
        return False
    new_risk_percent = (trade['Risk Dollar'] / portfolio_size) * 100
    total_risk_after_trade = current_risk_percent + new_risk_percent
    if total_risk_after_trade > (MAX_DAILY_LOSS * 100):
        print(f"Trade for {trade['Stock']} skipped due to exceeding max risk limits.")
        return False
    print(colored(f"Executing fractional trade for: {trade['Stock']}, Simulated={simulated}, Amount: ${trade['Trade Amount']:.2f}", 'green'))
    if is_market_open() and not simulated:
        try:
            order_result = r.orders.order_buy_fractional_by_price(
                symbol=trade['Stock'],
                amountInDollars=trade['Trade Amount'],
                timeInForce='gfd',
                extendedHours=False,  
                jsonify=True
            )
            print(f"Order result: {order_result}")
            if isinstance(order_result, dict):
                order_id = order_result.get('id')
                if order_id:
                    order_status = check_order_status(order_id)
                    if order_status == 'filled':
                        trade['Trade Made'] = True
                        trade['Order Status'] = order_status
                        trade['Order ID'] = order_id
                        global_account_data['positions'][trade['Stock']] = {
                            'name': trade['Stock'],
                            'quantity': trade['Shares to Purchase'],
                            'price': trade['Share Price'],
                            'purchase_date': datetime.now().strftime("%Y-%m-%d"),  
                            'created_at': datetime.now().isoformat()  
                        }
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
        except Exception as e:
            print(f"Exception occurred while executing trade: {e}")
            return False
    else:
        print(f"Simulated or out-of-hours trade for {trade['Stock']}.")
        trade['Trade Made'] = True
        trade['Order Status'] = "Simulated"
        trade['Order ID'] = "SIM12345"
        global_account_data['positions'][trade['Stock']] = {
            'name': trade['Stock'],
            'quantity': trade['Shares to Purchase'],
            'price': trade['Share Price'],
            'purchase_date': datetime.now().strftime("%Y-%m-%d"),  
            'created_at': datetime.now().isoformat()  
        }
        return True
def send_trade_summary(top_trades, portfolio_size, current_risk_percent, open_trades, global_account_data, simulated=False):
    summary_message = "\n--- Trade Summary ---\n"
    mode = "SIMULATED" if simulated else "LIVE"
    summary_message += f"Mode: {mode}\n\n"
    if 'sales' in global_account_data:
        summary_message += "--- Sales Made ---\n"
        for sale in global_account_data['sales']:
            sale_type = "Profit" if sale['profit'] else "Loss"
            summary_message += f"{sale['symbol']} - {sale_type} at ${sale['sale_price']:.2f} on {sale['sale_time']}\n"
        summary_message += "\n"
    summary_message += "--- Top Trades ---\n"
    for trade in top_trades:
        atr = trade.get('ATR', 0)
        atr_percent = trade.get('ATR Percent', 0)
        trade_amount = trade.get('Trade Amount', 0)
        shares_to_purchase = trade.get('Shares to Purchase', 0)
        purchase_price = trade.get('Share Price', 0)
        stop_loss = purchase_price - (2 * atr)
        stop_limit = purchase_price + (2 * atr)
        summary_message += f"Stock: {trade['Stock']}\n"
        summary_message += f"Trade Made: {trade['Trade Made']}\n"
        if trade['Trade Made']:
            summary_message += f"Trade Amount: ${trade_amount:.2f}\n"
            summary_message += f"Shares to Purchase: {shares_to_purchase:.2f} shares\n"
            summary_message += f"Potential Gain: ${trade['Potential Gain']:.2f}\n"
            summary_message += f"Risk Percent: {trade['Risk Percent']:.2f}%\n"
            summary_message += f"ATR: ${atr:.2f} (ATR Percent: {atr_percent:.2f}%)\n"
            summary_message += f"Stop Loss: ${stop_loss:.2f}, Stop Limit: ${stop_limit:.2f}\n"
        summary_message += "\n"
    summary_message += f"\nPortfolio Size: ${portfolio_size:.2f}\n"
    summary_message += f"Current Risk: {current_risk_percent:.2f}%\n"
    summary_message += "\n--- Open Trades ---\n"
    for trade in open_trades:
        historical_data = fetch_historical_data(trade.symbol)
        atr = calculate_atr(historical_data)
        atr_percent = (atr / float(global_account_data['positions'][trade.symbol].get('average_buy_price', 0))) * 100
        current_price = float(global_account_data['positions'][trade.symbol].get('price', 0))
        purchase_price = float(global_account_data['positions'][trade.symbol].get('average_buy_price', 0))
        stop_loss = purchase_price - (2 * atr)
        stop_limit = purchase_price + (2 * atr)
        percent_to_stop_loss = ((current_price - stop_loss) / current_price) * 100
        percent_to_stop_limit = ((stop_limit - current_price) / current_price) * 100
        created_at = global_account_data['positions'][trade.symbol].get('created_at', 'N/A')
        if created_at != 'N/A':
            try:
                created_date = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                days_held = (datetime.now() - created_date).days
            except ValueError:
                days_held = 0
        else:
            days_held = 0
        summary_message += f"Symbol: {trade.symbol}\n"
        summary_message += f"Quantity: {trade.quantity:.4f}\n"
        summary_message += f"Purchase Price: ${purchase_price:.2f}\n"
        summary_message += f"Price: ${current_price:.2f}\n"
        summary_message += f"Risk: ${trade.risk:.2f}\n"
        summary_message += f"ATR: ${atr:.2f} (ATR Percent: {atr_percent:.2f}%)\n"
        summary_message += f"Stop Loss: ${stop_loss:.2f} ({percent_to_stop_loss:.2f}% move from current price)\n"
        summary_message += f"Stop Limit: ${stop_limit:.2f} ({percent_to_stop_limit:.2f}% move from current price)\n"
        summary_message += f"Created At: {created_at}\n"
        summary_message += f"Days Held: {days_held} days\n"
        summary_message += "\n"
    send_text_message(summary_message)
def check_positions_against_atr(global_account_data):
    """
    Checks all open positions to see if they have crossed their ATR-based stop loss or stop limit.
    If crossed, it triggers a market order to close the position and logs the sale.
    """
    positions = global_account_data['positions']
    positions_closed = False  
    for symbol, data in positions.items():
        quantity = float(data.get('quantity', 0))
        purchase_price = float(data.get('average_buy_price', 0))
        current_price = float(data.get('price', 0))
        historical_data = fetch_historical_data(symbol)
        atr = calculate_atr(historical_data)
        stop_loss = purchase_price - (2 * atr)
        stop_limit = purchase_price + (2 * atr)
        if current_price <= stop_loss:
            print(f"Position for {symbol} has hit the stop loss at ${stop_loss:.2f}. Closing the position.")
            close_trade(symbol, quantity, sale_type="Loss", sale_price=current_price)
            positions_closed = True  
        elif current_price >= stop_limit:
            print(f"Position for {symbol} has hit the stop limit at ${stop_limit:.2f}. Closing the position.")
            close_trade(symbol, quantity, sale_type="Profit", sale_price=current_price)
            positions_closed = True  
    if not positions_closed:
        print("No positions have hit the ATR stop loss or stop limit.")
def close_trades_open_for_ten_days(positions):
    """
    Checks if any trades have been open for more than 10 days.
    If so, closes the trades and logs the sales.
    """
    trades_closed = False  
    for symbol, data in positions.items():
        purchase_date_str = data.get('purchase_date')
        if purchase_date_str:
            purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d")
            days_held = (datetime.now() - purchase_date).days
            if days_held > 10:
                quantity = float(data.get('quantity', 0))
                current_price = float(data.get('price', 0))
                print(f"Trade for {symbol} has been open for more than 10 days. Closing the position.")
                close_trade(symbol, quantity, sale_price=current_price)
                trades_closed = True  
    if not trades_closed:
        print("No trades open more than 10 days.")
def close_trade(trade):
    try:
        result = r.orders.order_sell_market(trade.symbol, trade.quantity)
        if result and 'id' in result:
            print(f"Trade {trade.symbol} closed successfully.")
            current_price = float(global_account_data['positions'][trade.symbol].get('price', 0))
            purchase_price = float(global_account_data['positions'][trade.symbol].get('average_buy_price', 0))
            profit = current_price > purchase_price  
            add_sale_to_global_data(trade.symbol, profit, current_price)
        else:
            print(f"Failed to close trade for {trade.symbol}. Response: {result}")
    except Exception as e:
        print(f"Exception occurred while closing trade: {e}")
def add_sale_to_global_data(symbol, profit, sale_price):
    """
    Logs the sale of a stock position in the global account data, marking whether the sale was for a profit or loss.
    :param symbol: The stock symbol of the sold position.
    :param profit: Boolean value indicating if the sale was profitable (True) or a loss (False).
    :param sale_price: The price at which the stock was sold.
    """
    if 'sales' not in global_account_data:
        global_account_data['sales'] = []  
    sale_info = {
        'symbol': symbol,
        'profit': profit,
        'sale_price': sale_price,
        'sale_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
    }
    global_account_data['sales'].append(sale_info)
    sale_type = "profit" if profit else "loss"
    print(f"Sale made for {sale_type}: {symbol} at ${sale_price:.2f}")
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
                    matched_orders[stock_symbol] = created_at  
            else:
                print("No instrument URL found in order.")
    else:
        print("No stock orders found.")
    return matched_orders

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
def order_buy_market(symbol, quantity):
    try:
        order = r.orders.order_buy_market(symbol, quantity)
        order_id = order.get('id')  
        return order_id
    except Exception as e:
        print(f"Error placing market order: {e}")
        return None
def order_sell_market(symbol, quantity):
    try:
        order = r.orders.order_sell_market(symbol, quantity)
        return order
    except Exception as e:
        print(f"Error placing market sell order: {e}")
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

