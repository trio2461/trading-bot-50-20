# utils/settings.py

# General Settings
SIMULATED = True  # Set this to False when going live
SIMULATED_PORTFOLIO_SIZE = 20000  # Portfolio size when running in simulated mode
MAX_DAILY_LOSS = 0.065  # Max daily loss limit as a percentage of the portfolio
PHONE_NUMBER = '252-571-5303'

# Data Source Settings
USE_CSV_DATA = True  # Set to True to use CSV data; False to use top movers
USE_NASDAQ_DATA = True  # Set to True to use NASDAQ data only
USE_SP500_DATA = True  # Set to True to use S&P 500 data only

# Trading Strategy Settings
ATR_THRESHOLDS = (3.0, 4.0, 5.0)  # ATR thresholds for classifying ATR percentages

# EXUDE_LIST	= (STEC)  # List of stocks to exude from trading
# this is