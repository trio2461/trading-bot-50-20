# utils/settings.py

# General Settings
SIMULATED = True  # Set this to False when going live
SIMULATED_PORTFOLIO_SIZE = 10000  # Portfolio size when running in simulated mode
MAX_DAILY_LOSS = 0.06  # Max daily loss limit as a percentage of the portfolio

# Data Source Settings
USE_CSV_DATA = True  # Set to True to use CSV data; False to use top movers
USE_NASDAQ_DATA = False  # Set to True to use NASDAQ data only
USE_SP500_DATA = True  # Set to True to use S&P 500 data only

# Trading Strategy Settings
ATR_THRESHOLDS = (3.0, 4.0, 5.0)  # ATR thresholds for classifying ATR percentages

# Eventually I'd like to make the data source more dynamic and the max daily loss dynamic, so if it's set to .05 I cant take a different amount of trades, how would that work with my 1/5 1/4, 1/3 set up? Well, they would still be .02 percent loss of portfolio, it would just be only 2 trades allowed. I couldn't really do 4 trades with .08 because then all the portfolio would be used up? Or no, if I did .08 on a 3% ATR trade, which would be 6% of the loss in the trade, losing me .02 percent, in order for that to happen, I'd have to use 1/3 of the portfolio, by hard coding this atr percentage, you really can only do 3 trades, is that right? well, yes. unless you do 2% atr * 2, maybe? lets see, if you only take the 5%'s you can take 5 trades, because (.02 * 1000)/2* which would be 10% = $200 which would mean you could take 1000/200 in trades. 1000/200 = 5. But does the code know that. I guess we also need to make sure the bot also checks if this uses all your funds or not, something like, if is not more than daily risk and is not more than all the funds, then trade.