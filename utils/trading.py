# utils/trading.py
import robin_stocks.robinhood as r
from utils.analysis import moving_average, calculate_atr, detect_recent_crossover, check_recent_crossovers
from utils.api import fetch_historical_data, order_buy_market, get_positions
from utils.settings import SIMULATED, MAX_DAILY_LOSS, ATR_THRESHOLDS, PHONE_NUMBER
from utils.send_message import send_text_message
from utils.trade_state import TradeState,calculate_current_risk, get_open_trades
from termcolor import colored
from datetime import datetime

def is_market_open():
    from datetime import datetime, time
    now = datetime.now().time()
    market_open = time(9, 30)
    market_close = time(16, 0)
    return market_open <= now <= market_close


def analyze_stock(stock, results, portfolio_size, current_risk, simulated=SIMULATED, atr_thresholds=ATR_THRESHOLDS):
    historicals = fetch_historical_data(stock)
    
    if not historicals or len(historicals) < 50:  # Ensure enough data for moving averages
        print(f"Not enough data for {stock}. Skipping...")
        return False
    
    closing_prices = [float(day['close_price']) for day in historicals]
    ma_20 = moving_average(closing_prices, 20)
    ma_50 = moving_average(closing_prices, 50)
    
    crossover_signal = detect_recent_crossover(ma_20[-len(ma_50):], ma_50, days=5)
    
    atr = calculate_atr(historicals)
    atr_percent = (atr / closing_prices[-1]) * 100 if closing_prices[-1] != 0 else 0
    share_price = closing_prices[-1]  # Latest share price
    
    # Filter out stocks with an ATR percent less than 3%
    if atr_percent < 3.0:
        print(f"{stock} skipped due to ATR percent being less than 3% ({atr_percent:.2f}%).")
        return False
    
    # Classify ATR into 3%, 4%, or 5%
    if atr_percent < 3.5:
        classified_atr_percent = 3.0
    elif atr_percent < 4.5:
        classified_atr_percent = 4.0
    else:
        classified_atr_percent = 5.0

    # Only consider trades if the crossover is bullish and the ATR is within the desired range
    if crossover_signal == "Bullish Crossover" and classified_atr_percent in atr_thresholds:
        print(f"Eligible Bullish Crossover found for {stock} with Classified ATR: {classified_atr_percent}%")
        
        # Calculate purchase amount based on the classified ATR
        two_atr = 2 * (classified_atr_percent / 100)
        purchase_amount = (0.02 * portfolio_size) / two_atr
        shares_to_purchase = purchase_amount / share_price  # Calculate the number of shares
        potential_loss = purchase_amount * two_atr
        potential_gain = potential_loss  # 1:1 risk-reward ratio
        risk_percent = (potential_loss / portfolio_size) * 100  # Calculate risk percentage of the portfolio

        # Ensure the risk and portfolio limits are not exceeded
        if potential_loss <= portfolio_size * 0.02 and current_risk + potential_loss <= MAX_DAILY_LOSS * portfolio_size:
            results.append({
                'Stock': stock,
                'ATR': atr,
                'ATR Percent': atr_percent,
                'ATR * 2': two_atr * 100,  # Include ATR * 2 in the results
                'Share Price': share_price,
                'Eligible for Trade': True,
                'Trade Made': False,  # Initially mark as not attempted
                'Order Status': "Not Attempted",  # Add order status
                'Order ID': None,
                'Trade Amount': purchase_amount,
                'Shares to Purchase': shares_to_purchase,
                'Potential Gain': potential_gain,
                'Risk Percent': risk_percent,
                'Risk Dollar': potential_loss,
                'Reason': "Criteria met"
            })
            current_risk += potential_loss  # Update the current risk right after adding a valid trade
            print(f"Adding eligible trade for {stock}.")
        else:
            print(f"Skipping {stock} due to risk exceeding limits.")
    else:
        # Print only if the stock had a crossover but didn't meet other criteria
        if crossover_signal == "Bullish Crossover":
            print(f"{stock} had a Bullish Crossover but was not eligible due to ATR or risk criteria.\n")

    return True  # Return True to indicate the stock was analyzed


def execute_trade(trade, portfolio_size, current_risk_percent, simulated):
    positions = get_positions()
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
                        # Save the purchase date to global_account_data
                        global_account_data['positions'][trade['Stock']] = {
                            'name': trade['Stock'],
                            'quantity': trade['Shares to Purchase'],
                            'price': trade['Share Price'],
                            'purchase_date': datetime.now().strftime("%Y-%m-%d")  # Store the current date
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
        return True


# Fixing the summary report to correctly reflect current risk
def send_trade_summary(top_trades, portfolio_size, current_risk_percent, open_trades, simulated=SIMULATED):
    summary_message = "\n--- Trade Summary ---\n"
    
    # Indicate if the trades are simulated or live
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
        summary_message += "\n"  # Adding a blank line between each trade
    
    # Display portfolio size and current risk as a percentage of the portfolio
    summary_message += f"\nPortfolio Size: ${portfolio_size:.2f}\n"
    summary_message += f"Current Risk: {current_risk_percent:.2f}%\n"

    # Adding details of open trades
    summary_message += "\n--- Open Trades ---\n"
    for trade in open_trades:
        summary_message += f"Symbol: {trade.symbol}\n"
        summary_message += f"Quantity: {trade.quantity}\n"
        summary_message += f"Price: ${trade.price:.2f}\n"
        summary_message += f"Risk: {trade.risk}\n"
        summary_message += f"Side: {trade.side.capitalize()}\n"
        summary_message += "\n"  # Adding a blank line between each trade

    send_text_message(summary_message, phone_number=PHONE_NUMBER)


def check_open_positions_sell_points():
    open_positions = r.account.build_holdings()  # Get open positions
    for symbol, data in open_positions.items():
        current_price = float(data['price'])  # Current market price
        quantity = float(data['quantity'])
        purchase_price = float(data['average_buy_price'])  # Initial purchase price

        historical_data = fetch_historical_data(symbol)
        atr = calculate_atr(historical_data)  # Calculate ATR
        atr_percent = (atr / purchase_price) * 100

        # Determine which ATR category (3%, 4%, 5%) the stock falls under
        if atr_percent < 3.5:
            atr_multiple = 3
        elif atr_percent < 4.5:
            atr_multiple = 4
        else:
            atr_multiple = 5

        sell_point = purchase_price + (2 * (atr_multiple / 100) * purchase_price)  # 2 * ATR above purchase price

        if current_price >= sell_point:
            print(f"Selling {symbol} at {current_price} (Sell point: {sell_point})")
            order = order_sell_market(symbol, quantity)
            print(f"Sell order placed for {symbol}: {order}")
        else:
            print(f"{symbol} has not hit the sell point yet. Current price: {current_price}, Sell point: {sell_point}")