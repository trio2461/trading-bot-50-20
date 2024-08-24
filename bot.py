import robin_stocks.robinhood as r
import os
import pandas as pd
from datetime import datetime, time

# Login to Robinhood using credentials from environment variables
def login_to_robinhood():
    username = os.getenv('ROBINHOOD_USERNAME')
    password = os.getenv('ROBINHOOD_PASSWORD')
    r.login(username=username, password=password)

# Fetch and display the portfolio size
def get_portfolio_size(simulated=True, simulated_size=1000):
    if simulated:
        return simulated_size
    else:
        portfolio = r.profiles.load_account_profile(info='portfolio_cash')
        return float(portfolio)

# Extract stock symbols from a CSV file
def get_stock_symbols_from_csv(file_path='nasdaq100_full.csv'):
    df = pd.read_csv(file_path)
    stock_symbols = df['Ticker'].tolist()
    return stock_symbols

# Fetch historical data for a stock with error handling
def fetch_historical_data(stock, interval='day', span='3month'):
    try:
        return r.stocks.get_stock_historicals(stock, interval=interval, span=span)
    except r.exceptions.APIError as e:
        return None

# Calculate moving averages
def moving_average(data, period):
    return [sum(data[i:i+period])/period for i in range(len(data)-period+1)]

# Calculate the Average True Range (ATR)
def calculate_atr(historicals, period=14):
    tr_list = []
    for i in range(1, len(historicals)):
        high_low = float(historicals[i]['high_price']) - float(historicals[i]['low_price'])
        high_close = abs(float(historicals[i]['high_price']) - float(historicals[i-1]['close_price']))
        low_close = abs(float(historicals[i]['low_price']) - float(historicals[i-1]['close_price']))
        true_range = max(high_low, high_close, low_close)
        tr_list.append(true_range)
    atr = sum(tr_list[-period:]) / period
    return atr

# Detect crossover signals within a lookback period of 3 days
def detect_crossover(ma_short, ma_long, lookback_period=3):
    if len(ma_short) < lookback_period + 1 or len(ma_long) < lookback_period + 1:
        return None
    for i in range(1, lookback_period + 1):
        if ma_short[-i-1] <= ma_long[-i-1] and ma_short[-i] > ma_long[-i]:
            return "Bullish Crossover"
        elif ma_short[-i-1] >= ma_long[-i-1] and ma_short[-i] < ma_long[-i]:
            return "Bearish Crossover"
    return None

# Check if there was a recent opposite crossover to avoid range-bound stocks
def check_recent_crossovers(stock, ma_short, ma_long):
    if len(ma_short) < 5 or len(ma_long) < 5:
        return True  # Skip check if not enough data
    for i in range(1, 5):
        if detect_crossover(ma_short[-i:], ma_long[-i:]) == "Bearish Crossover":
            return False
    return True

# Check if it is within regular trading hours
def is_market_open():
    now = datetime.now().time()
    market_open = time(9, 30)
    market_close = time(16, 0)
    return market_open <= now <= market_close

# Analyze a single stock
def analyze_stock(stock, results, portfolio_size, daily_loss_limit, simulated=True):
    historicals = fetch_historical_data(stock)
    
    if not historicals or len(historicals) < 50:  # Ensure enough data for moving averages
        return
    
    closing_prices = [float(day['close_price']) for day in historicals]
    ma_20 = moving_average(closing_prices, 20)
    ma_50 = moving_average(closing_prices, 50)
    
    crossover_signal = detect_crossover(ma_20[-len(ma_50):], ma_50, lookback_period=3)
    
    atr = calculate_atr(historicals)
    atr_percent = (atr / closing_prices[-1]) * 100 if closing_prices[-1] != 0 else 0
    
    if not check_recent_crossovers(stock, ma_20, ma_50):
        return
    
    trade_made = False
    trade_amount = 0
    risk_per_trade = portfolio_size * 0.02
    potential_loss = atr * 2
    trade_amount = risk_per_trade / potential_loss if potential_loss != 0 else 0  # Handle division by zero
    
    potential_gain = atr * trade_amount  # Potential gain in dollars
    risk_percent = (potential_loss / portfolio_size) * 100  # Calculate risk percentage of the portfolio

    if potential_loss > risk_per_trade:
        return
    elif daily_loss_limit + potential_loss > portfolio_size * 0.06:
        return
    else:
        if crossover_signal in ["Bullish Crossover", "Bearish Crossover"] and atr >= 0.04 * closing_prices[-1]:  # Adjusted to 4%
            if is_market_open():
                trade_made = True
                if simulated:
                    print(f"Simulated trade: {'Buy' if crossover_signal == 'Bullish Crossover' else 'Sell'} {stock} for {trade_amount:.2f} shares.")
                else:
                    if crossover_signal == "Bullish Crossover":
                        r.orders.order_buy_market(stock, quantity=int(trade_amount))
                    else:
                        r.orders.order_sell_market(stock, quantity=int(trade_amount))
                daily_loss_limit += potential_loss
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
        'Reason': "After hours" if not trade_made and not is_market_open() else "Criteria not met"
    })

# Main function to run the bot
def main():
    login_to_robinhood()
    simulated = True
    portfolio_size = get_portfolio_size(simulated)
    daily_loss_limit = 0
    stock_symbols = get_stock_symbols_from_csv()
    results = []
    
    for stock in stock_symbols:
        analyze_stock(stock, results, portfolio_size, daily_loss_limit, simulated=simulated)
    
    results.sort(key=lambda x: x['ATR Percent'], reverse=True)

    print("\n--- Summary of Bullish Crossovers and Trades ---")
    for result in results:
        if result['Signal'] == "Bullish Crossover":
            print(f"{result['Stock']}: Trade Made: {result['Trade Made']}, Trade Amount: {result['Trade Amount']:.2f} shares, Potential Gain: ${result['Potential Gain']:.2f}, Risk: {result['Risk Percent']:.2f}%, ATR: {result['ATR']:.2f} ({result['ATR Percent']:.2f}%), Reason: {result['Reason']}")
    
    print(f"\n--- Portfolio Size at the End: ${portfolio_size} ---")

if __name__ == "__main__":
    main()
