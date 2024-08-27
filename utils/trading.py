# utils/trading.py
from utils.analysis import moving_average, calculate_atr, detect_recent_crossover, check_recent_crossovers
from utils.api import fetch_historical_data, order_buy_market
from utils.settings import SIMULATED, MAX_DAILY_LOSS, ATR_THRESHOLDS  # Corrected import
from termcolor import colored  # Import termcolor for colored output

def is_market_open():
    from datetime import datetime, time
    now = datetime.now().time()
    market_open = time(9, 30)
    market_close = time(16, 0)
    return market_open <= now <= market_close

def analyze_stock(stock, results, portfolio_size, current_risk, simulated=SIMULATED, atr_thresholds=ATR_THRESHOLDS):
    print(f"\n--- Analyzing {stock} ---")
    historicals = fetch_historical_data(stock)
    
    if not historicals or len(historicals) < 50:  # Ensure enough data for moving averages
        print(f"Not enough data for {stock}. Skipping...")
        return False
    
    closing_prices = [float(day['close_price']) for day in historicals]
    ma_20 = moving_average(closing_prices, 20)
    ma_50 = moving_average(closing_prices, 50)
    
    crossover_signal = detect_recent_crossover(ma_20[-len(ma_50):], ma_50, days=5)
    print(f"Crossover Signal: {crossover_signal}")
    
    atr = calculate_atr(historicals)
    atr_percent = (atr / closing_prices[-1]) * 100 if closing_prices[-1] != 0 else 0
    share_price = closing_prices[-1]  # Latest share price
    print(f"ATR: {atr:.2f} ({atr_percent:.2f}% of the stock price)")
    
    # Classify ATR into 3%, 4%, or 5%
    if atr_percent < 3.5:
        classified_atr_percent = 3.0
    elif atr_percent < 4.5:
        classified_atr_percent = 4.0
    else:
        classified_atr_percent = 5.0
        
    if classified_atr_percent == 5.0:
        print(colored(f"Classified ATR: {classified_atr_percent}% of the stock price", "green"))
    else:
        print(f"Classified ATR: {classified_atr_percent}% of the stock price")

    # Calculate purchase amount based on the classified ATR
    two_atr = 2 * (classified_atr_percent / 100)
    purchase_amount = (0.02 * portfolio_size) / two_atr
    shares_to_purchase = purchase_amount / share_price  # Calculate the number of shares
    print(f"Purchase Amount: ${purchase_amount:.2f} based on 2 * ATR: {two_atr * 100:.2f}%")
    print(f"Share Price: ${share_price:.2f}, Purchase Amount in Shares: {shares_to_purchase:.2f} shares")
    
    if not check_recent_crossovers(stock, ma_20, ma_50):
        print(f"{stock} skipped due to recent conflicting crossovers.")
        return False
    
    eligible_for_trade = False
    trade_made = False
    potential_loss = purchase_amount * two_atr
    potential_gain = potential_loss  # 1:1 risk-reward ratio
    
    risk_percent = (potential_loss / portfolio_size) * 100  # Calculate risk percentage of the portfolio

    if classified_atr_percent < atr_thresholds[0] or classified_atr_percent > atr_thresholds[-1]:
        print(f"{stock} skipped due to ATR not within the acceptable range ({atr_thresholds}).")
        return False

    if potential_loss > portfolio_size * 0.02 or current_risk + potential_loss > MAX_DAILY_LOSS * portfolio_size:  # Updated variable name
        print(f"Skipping {stock} due to risk exceeding limits.")
        return False
    
    if crossover_signal == "Bullish Crossover":
        eligible_for_trade = True
        if is_market_open() and not simulated:
            # Execute live trade
            order_result = order_buy_market(stock, int(shares_to_purchase))
            if order_result:
                trade_made = True
                current_risk += potential_loss  # Apply the risk only if the trade is made
                print(f"Trade executed for {stock}.")
        else:
            # Simulate or record out-of-hours trade
            print(f"Simulated or out-of-hours trade for {stock}.")
            trade_made = True
            current_risk += potential_loss  # Apply the risk in simulation as well

    # Record the result with proper flags
    results.append({
        'Stock': stock,
        'ATR': atr,
        'ATR Percent': atr_percent,
        'Share Price': share_price,
        'Eligible for Trade': eligible_for_trade,
        'Trade Made': trade_made,
        'Trade Amount': purchase_amount,
        'Shares to Purchase': shares_to_purchase,
        'Potential Gain': potential_gain,
        'Risk Percent': risk_percent,
        'Risk Dollar': potential_loss,
        'Reason': "Criteria met" if eligible_for_trade else "Criteria not met"
    })

    return trade_made  # Return whether a trade was actually made

# from utils.analysis import moving_average, calculate_atr, detect_recent_crossover, check_recent_crossovers
# from utils.api import fetch_historical_data, order_buy_market
# from utils.settings import SIMULATED, MAX_DAILY_LOSS, ATR_THRESHOLDS  # Import settings
# from termcolor import colored  # Import termcolor for colored output

# def is_market_open():
#     from datetime import datetime, time
#     now = datetime.now().time()
#     market_open = time(9, 30)
#     market_close = time(16, 0)
#     return market_open <= now <= market_close

# def analyze_stock(stock, results, portfolio_size, current_risk, simulated=SIMULATED, atr_thresholds=ATR_THRESHOLDS):
#     print(f"\n--- Analyzing {stock} ---")
#     historicals = fetch_historical_data(stock)
    
#     if not historicals or len(historicals) < 50:  # Ensure enough data for moving averages
#         print(f"Not enough data for {stock}. Skipping...")
#         return False
    
#     closing_prices = [float(day['close_price']) for day in historicals]
#     ma_20 = moving_average(closing_prices, 20)
#     ma_50 = moving_average(closing_prices, 50)
    
#     crossover_signal = detect_recent_crossover(ma_20[-len(ma_50):], ma_50, days=5)
#     print(f"Crossover Signal: {crossover_signal}")
    
#     atr = calculate_atr(historicals)
#     atr_percent = (atr / closing_prices[-1]) * 100 if closing_prices[-1] != 0 else 0
#     share_price = closing_prices[-1]  # Latest share price
#     print(f"ATR: {atr:.2f} ({atr_percent:.2f}% of the stock price)")
    
#     # Classify ATR into 3%, 4%, or 5%
#     if atr_percent < 3.5:
#         classified_atr_percent = 3.0
#     elif atr_percent < 4.5:
#         classified_atr_percent = 4.0
#     else:
#         classified_atr_percent = 5.0
        
#     if classified_atr_percent == 5.0:
#         print(colored(f"Classified ATR: {classified_atr_percent}% of the stock price", "green"))
#     else:
#         print(f"Classified ATR: {classified_atr_percent}% of the stock price")

#     # Calculate purchase amount based on the classified ATR
#     two_atr = 2 * (classified_atr_percent / 100)
#     purchase_amount = (0.02 * portfolio_size) / two_atr
#     shares_to_purchase = purchase_amount / share_price  # Calculate the number of shares
#     print(f"Purchase Amount: ${purchase_amount:.2f} based on 2 * ATR: {two_atr * 100:.2f}%")
#     print(f"Share Price: ${share_price:.2f}, Purchase Amount in Shares: {shares_to_purchase:.2f} shares")
    
#     if not check_recent_crossovers(stock, ma_20, ma_50):
#         print(f"{stock} skipped due to recent conflicting crossovers.")
#         return False
    
#     eligible_for_trade = False
#     trade_made = False
#     potential_loss = purchase_amount * two_atr
#     potential_gain = potential_loss  # 1:1 risk-reward ratio
    
#     risk_percent = (potential_loss / portfolio_size) * 100  # Calculate risk percentage of the portfolio

#     if classified_atr_percent < atr_thresholds[0] or classified_atr_percent > atr_thresholds[-1]:
#         print(f"{stock} skipped due to ATR not within the acceptable range ({atr_thresholds}).")
#         return False

#     if potential_loss > portfolio_size * 0.02 or current_risk + potential_loss > MAX_DAILY_RISK * portfolio_size:
#         print(f"Skipping {stock} due to risk exceeding limits.")
#         return False
    
#     if crossover_signal == "Bullish Crossover":
#         eligible_for_trade = True
#         if is_market_open() and not simulated:
#             # Execute live trade
#             order_result = order_buy_market(stock, int(shares_to_purchase))
#             if order_result:
#                 trade_made = True
#                 current_risk += potential_loss  # Apply the risk only if the trade is made
#                 print(f"Trade executed for {stock}.")
#         else:
#             # Simulate or record out-of-hours trade
#             print(f"Simulated or out-of-hours trade for {stock}.")
#             trade_made = True
#             current_risk += potential_loss  # Apply the risk in simulation as well

#     # Record the result with proper flags
#     results.append({
#         'Stock': stock,
#         'ATR': atr,
#         'ATR Percent': atr_percent,
#         'Share Price': share_price,
#         'Eligible for Trade': eligible_for_trade,
#         'Trade Made': trade_made,
#         'Trade Amount': purchase_amount,
#         'Shares to Purchase': shares_to_purchase,
#         'Potential Gain': potential_gain,
#         'Risk Percent': risk_percent,
#         'Risk Dollar': potential_loss,
#         'Reason': "Criteria met" if eligible_for_trade else "Criteria not met"
#     })

#     return trade_made  # Return whether a trade was actually made
 