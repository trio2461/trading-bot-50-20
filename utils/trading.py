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


def send_trade_summary(top_trades, portfolio_size, current_risk_percent, open_trades, global_account_data, simulated=False):
    summary_message = "\n--- Trade Summary ---\n"
    mode = "SIMULATED" if simulated else "LIVE"
    summary_message += f"Mode: {mode}\n\n"

    # Include the sales information
    if 'sales' in global_account_data:
        summary_message += "--- Sales Made ---\n"
        for sale in global_account_data['sales']:
            sale_type = "Profit" if sale['profit'] else "Loss"
            summary_message += f"{sale['symbol']} - {sale_type} at ${sale['sale_price']:.2f} on {sale['sale_time']}\n"
        summary_message += "\n"

    for trade in top_trades:
        atr = trade.get('ATR', 0)
        atr_percent = trade.get('ATR Percent', 0)
        trade_amount = trade.get('Trade Amount', 0)
        shares_to_purchase = trade.get('Shares to Purchase', 0)
        purchase_price = trade.get('Share Price', 0)

        # Calculating stop loss and stop limit
        stop_loss = purchase_price - (2 * atr)
        stop_limit = purchase_price + (2 * atr)

        # Calculate percentage moves to stop loss and stop limit from the **current price**
        current_price = float(global_account_data['positions'][trade['Stock']].get('price', purchase_price))  
        percent_to_stop_loss = ((current_price - stop_loss) / current_price) * 100
        percent_to_stop_limit = ((stop_limit - current_price) / current_price) * 100

        summary_message += f"Stock: {trade['Stock']}\n"
        summary_message += f"Trade Made: {trade['Trade Made']}\n"
        summary_message += f"Trade Amount: ${trade_amount:.2f}\n"
        summary_message += f"Shares to Purchase: {shares_to_purchase:.2f} shares\n"
        summary_message += f"Potential Gain: ${trade['Potential Gain']:.2f}\n"
        summary_message += f"Risk Percent: {trade['Risk Percent']:.2f}%\n"
        summary_message += f"Risk Dollar: ${trade['Risk Dollar']:.2f}\n"
        summary_message += f"ATR: ${atr:.2f} (Average True Range in dollars)\n"
        summary_message += f"ATR Percent: {atr_percent:.2f}% (ATR as percent of the stock price)\n"
        summary_message += f"Stop Loss: ${stop_loss:.2f} ({percent_to_stop_loss:.2f}% move from current price)\n"
        summary_message += f"Stop Limit: ${stop_limit:.2f} ({percent_to_stop_limit:.2f}% move from current price)\n"
        summary_message += "\n"

    summary_message += f"\nPortfolio Size: ${portfolio_size:.2f}\n"
    summary_message += f"Current Risk: {current_risk_percent:.2f}%\n"
    summary_message += "\n--- Open Trades ---\n"

    # Processing open trades
    for trade in open_trades:
        # Fetch ATR for each open trade
        historical_data = fetch_historical_data(trade.symbol)
        atr = calculate_atr(historical_data)
        atr_percent = (atr / float(global_account_data['positions'][trade.symbol].get('average_buy_price', 0))) * 100

        # Price and stop loss/limit calculations
        current_price = float(global_account_data['positions'][trade.symbol].get('price', 0))
        purchase_price = float(global_account_data['positions'][trade.symbol].get('average_buy_price', 0))

        stop_loss = purchase_price - (2 * atr)
        stop_limit = purchase_price + (2 * atr)

        percent_to_stop_loss = ((current_price - stop_loss) / current_price) * 100
        percent_to_stop_limit = ((stop_limit - current_price) / current_price) * 100

        summary_message += f"Symbol: {trade.symbol}\n"
        summary_message += f"Quantity: {trade.quantity:.4f}\n"
        summary_message += f"Purchase Price: ${purchase_price:.2f}\n"
        summary_message += f"Price: ${current_price:.2f}\n"
        summary_message += f"Risk: ${trade.risk:.2f}\n"
        summary_message += f"Side: {trade.side.capitalize()}\n"
        summary_message += f"ATR: ${atr:.2f} (Average True Range in dollars)\n"
        summary_message += f"ATR Percent: {atr_percent:.2f}% (ATR as percent of stock price)\n"
        summary_message += f"Stop Loss: ${stop_loss:.2f} ({percent_to_stop_loss:.2f}% move from current price)\n"
        summary_message += f"Stop Limit: ${stop_limit:.2f} ({percent_to_stop_limit:.2f}% move from current price)\n"
        summary_message += "\n"

    # Send the message via text
    send_text_message(summary_message)

    
def check_open_positions_sell_points():
    open_positions = r.account.build_holdings()  
    open_trades = get_open_trades(open_positions)  

    for trade in open_trades:
        current_price = float(global_account_data['positions'][trade.symbol].get('price', 0))

        if current_price >= trade.stop_limit:
            print(f"Selling {trade.symbol} at {current_price} (Stop Limit: {trade.stop_limit})")
            order = order_sell_market(trade.symbol, trade.quantity)  
            print(f"Sell order placed for {trade.symbol}: {order}")

            # Determine if sale was for a profit
            profit = current_price > trade.purchase_price
            add_sale_to_global_data(trade.symbol, profit, current_price)
        
        elif current_price <= trade.stop_loss:
            print(f"Selling {trade.symbol} at {current_price} (Stop Loss: {trade.stop_loss})")
            order = order_sell_market(trade.symbol, trade.quantity)  
            print(f"Sell order placed for {trade.symbol}: {order}")

            # Determine if sale was for a profit
            profit = current_price > trade.purchase_price
            add_sale_to_global_data(trade.symbol, profit, current_price)
        
        else:
            print(f"{trade.symbol} has not hit the sell point yet. Current price: {current_price}, "
                  f"Stop Loss: {trade.stop_loss}, Stop Limit: {trade.stop_limit}")
            

def add_sale_to_global_data(symbol, profit, sale_price):
    if 'sales' not in global_account_data:
        global_account_data['sales'] = []

    sale_info = {
        'symbol': symbol,
        'profit': profit,
        'sale_price': sale_price,
        'sale_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    global_account_data['sales'].append(sale_info)

    # Log the sale information
    if profit:
        print(f"Sale made for profit: {symbol} at ${sale_price}")
    else:
        print(f"Sale made for a loss: {symbol} at ${sale_price}")