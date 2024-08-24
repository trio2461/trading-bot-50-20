# utils/analysis.py

# Calculate moving averages
def moving_average(data, period):
    return [sum(data[i:i+period])/period for i in range(len(data)-period+1)]

# Calculate the Average True Range (ATR)
# def calculate_atr(historicals, period=14):
#     tr_list = []
#     for i in range(1, len(historicals)):
#         high_low = float(historicals[i]['high_price']) - float(historicals[i]['low_price'])
#         high_close = abs(float(historicals[i]['high_price']) - float(historicals[i-1]['close_price']))
#         low_close = abs(float(historicals[i]['low_price']) - float(historicals[i-1]['close_price']))
#         true_range = max(high_low, high_close, low_close)
#         tr_list.append(true_range)
#     atr = sum(tr_list[-period:]) / period
#     return atr


# utils/analysis.py

def calculate_atr(historicals, period=14):
    tr_list = []
    
    # Calculate true ranges
    for i in range(1, len(historicals)):
        high_low = float(historicals[i]['high_price']) - float(historicals[i]['low_price'])
        high_close = abs(float(historicals[i]['high_price']) - float(historicals[i-1]['close_price']))
        low_close = abs(float(historicals[i]['low_price']) - float(historicals[i-1]['close_price']))
        true_range = max(high_low, high_close, low_close)
        tr_list.append(true_range)
    
    # Initial ATR
    initial_atr = sum(tr_list[:period]) / period
    
    # Subsequent ATRs
    atr_values = [initial_atr]
    for i in range(period, len(tr_list)):
        current_atr = (atr_values[-1] * (period - 1) + tr_list[i]) / period
        atr_values.append(current_atr)
    
    # Return the most recent ATR
    return atr_values[-1]

# Other functions (if any) in analysis.py...


# Detect crossover signals within the last 5 days
def detect_recent_crossover(ma_short, ma_long, days=5):
    if len(ma_short) < days + 1 or len(ma_long) < days + 1:
        return None
    for i in range(1, days + 1):
        if ma_short[-i-1] <= ma_long[-i-1] and ma_short[-i] > ma_long[-i]:
            return "Bullish Crossover"
    return None

# Check if there was a recent opposite crossover to avoid range-bound stocks
def check_recent_crossovers(stock, ma_short, ma_long):
    if len(ma_short) < 5 or len(ma_long) < 5:
        return True  # Skip check if not enough data
    for i in range(1, 5):
        if detect_recent_crossover(ma_short[-i:], ma_long[-i:]) == "Bearish Crossover":
            return False
    return True
