# utils/trading.py
from utils.analysis import moving_average, calculate_atr, detect_recent_crossover, check_recent_crossovers
from utils.api import fetch_historical_data

def is_market_open():
    from datetime import datetime, time
    now = datetime.now().time()
    market_open = time(9, 30)
    market_close = time(16, 0)
    return market_open <= now <= market_close

# Analyze a single stock
def analyze_stock(stock, results, portfolio_size, daily_loss_limit, simulated=True, atr_threshold=0.03):
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
    print(f"ATR: {atr:.2f} ({atr_percent:.2f}% of the stock price)")
    
    if not check_recent_crossovers(stock, ma_20, ma_50):
        print(f"{stock} skipped due to recent conflicting crossovers.")
        return False
    
    trade_made = False
    risk_per_trade = portfolio_size * 0.02
    potential_loss = atr * 2
    trade_amount = risk_per_trade / potential_loss if potential_loss != 0 else 0  # Handle division by zero
    
    # Calculate potential gain based on the ATR movement with a 2:1 reward-to-risk ratio
    reward_to_risk_ratio = 2
    potential_gain = trade_amount * atr * reward_to_risk_ratio  # Adjust this calculation based on your expected price movement
    risk_percent = (potential_loss / portfolio_size) * 100  # Calculate risk percentage of the portfolio
    
    # Ensure the ATR meets the 3% threshold
    if atr_percent < atr_threshold * 100:
        print(f"{stock} skipped due to ATR < {atr_threshold * 100}%.")
        return False

    if potential_loss > risk_per_trade or daily_loss_limit + potential_loss > portfolio_size * 0.06:
        print(f"Skipping {stock} due to risk exceeding limits.")
        return False
    else:
        if crossover_signal == "Bullish Crossover" and atr >= atr_threshold * closing_prices[-1]:
            if is_market_open():
                trade_made = True
                if not simulated:
                    r.orders.order_buy_market(stock, quantity=int(trade_amount))
                daily_loss_limit += potential_loss
                print(f"Trade executed for {stock}.")
            else:
                print(f"Not making trade for {stock} because it's after hours.")
        else:
            print(f"No trade placed for {stock} due to criteria not being met.")
    
    results.append({
        'Stock': stock,
        'Signal': crossover_signal,
        'ATR': atr,
        'ATR Percent': atr_percent,
        'Trade Made': trade_made,
        'Trade Amount': trade_amount,
        'Potential Gain': potential_gain,
        'Risk Percent': risk_percent,
        'Risk Dollar': potential_loss,  # Include dollar amount of the risk
        'Reason': "After hours" if not trade_made and not is_market_open() else "Criteria not met"
    })

    return trade_made  # Return whether a trade was actually made
