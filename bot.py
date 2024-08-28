# bot.py

from utils.api import login_to_robinhood, get_top_movers, fetch_historical_data, load_csv_data, sanitize_ticker_symbols, get_portfolio_size
from utils.trading import analyze_stock, send_trade_summary
from utils.trade_state import fetch_open_orders, calculate_current_risk, get_open_trades, TradeState
from utils.settings import SIMULATED, SIMULATED_PORTFOLIO_SIZE, MAX_DAILY_LOSS, USE_CSV_DATA, USE_NASDAQ_DATA, USE_SP500_DATA, ATR_THRESHOLDS
from termcolor import colored  # Import termcolor for colored output

def main():
    login_to_robinhood()
    simulated = SIMULATED  # Use setting from settings.py
    portfolio_size = get_portfolio_size(simulated, simulated_size=SIMULATED_PORTFOLIO_SIZE)
    max_daily_loss = portfolio_size * MAX_DAILY_LOSS  # Use setting from settings.py
    current_risk = 0  # Track the current risk as trades are made
    
    # Boolean options to control the data source
    use_csv_data = USE_CSV_DATA  # Use setting from settings.py
    use_nasdaq_data = USE_NASDAQ_DATA  # Use setting from settings.py
    use_sp500_data = USE_SP500_DATA  # Use setting from settings.py

    stock_symbols = []

    if use_csv_data:
        if use_nasdaq_data and not use_sp500_data:
            nasdaq_data = load_csv_data('nasdaq100_full.csv', 'nasdaq')
            nasdaq_data = sanitize_ticker_symbols(nasdaq_data)
            stock_symbols = nasdaq_data['Ticker'].tolist()
        elif use_sp500_data and not use_nasdaq_data:
            sp500_data = load_csv_data('sp500_companies.csv', 'sp500')
            sp500_data = sanitize_ticker_symbols(sp500_data)
            stock_symbols = sp500_data['Symbol'].tolist()
        elif use_nasdaq_data and use_sp500_data:
            nasdaq_data = load_csv_data('nasdaq100_full.csv', 'nasdaq')
            nasdaq_data = sanitize_ticker_symbols(nasdaq_data)
            sp500_data = load_csv_data('sp500_companies.csv', 'sp500')
            sp500_data = sanitize_ticker_symbols(sp500_data)
            stock_symbols = nasdaq_data['Ticker'].tolist() + sp500_data['Symbol'].tolist()
    else:
        stock_symbols = get_top_movers()

    results = []
    total_stocks_analyzed = 0
    total_trades_made = 0  # Counter for trades made

    # Fetch open orders and calculate current risk
    open_orders = fetch_open_orders()
    current_risk = calculate_current_risk(open_orders)

    # Analyze all stocks and collect valid trades
    for stock in stock_symbols:
        trade_made = analyze_stock(stock, results, portfolio_size, current_risk, atr_thresholds=ATR_THRESHOLDS, simulated=simulated)
        
        if trade_made:
            total_trades_made += 1

            if current_risk > max_daily_loss:
                print(colored(f"Daily loss limit exceeded after analyzing {stock}. No more trades will be made, but all stocks will be analyzed.", 'red'))
        
        total_stocks_analyzed += 1

    # Fetch and display current open trades
    openTrades = get_open_trades(open_orders)
    print(colored("\n--- Open Trades ---", 'magenta'))
    for trade in openTrades:
        print(trade)

    # List all trades that met the criteria
    print(colored("\n--- All Valid Trade Opportunities ---", 'cyan'))
    for result in results:
        if result['Eligible for Trade']:
            print(colored(f"{result['Stock']}: Trade Amount: ${result['Trade Amount']:.2f}, Shares to Purchase: {result['Shares to Purchase']:.2f} shares, ATR: {result['ATR']:.2f} ({result['ATR Percent']:.2f}%), Reason: {result['Reason']}", 'green'))

    # Sort results based on ATR Percent in descending order
    results.sort(key=lambda x: x['ATR Percent'], reverse=True)

    # Select the top three trades
    top_trades = [trade for trade in results if trade['Eligible for Trade']][:3]

    # Send the summary message with open trades info
    send_trade_summary(top_trades, portfolio_size, current_risk, openTrades)

    print(colored("\n--- Summary of Top Three Bullish Crossover Trades ---", 'yellow'))
    for result in top_trades:
        # Include ATR * 2 in the summary
        print(f"{result['Stock']}: {colored('Eligible for Trade:', 'blue')} {result['Eligible for Trade']}, {colored('Trade Made:', 'blue')} {result['Trade Made']}, Trade Amount: ${result['Trade Amount']:.2f}, Shares to Purchase: {result['Shares to Purchase']:.2f} shares, Potential Gain: ${result['Potential Gain']:.2f}, Risk: {result['Risk Percent']:.2f}% (${result['Risk Dollar']:.2f}), ATR: {result['ATR']:.2f} ({result['ATR Percent']:.2f}%), ATR * 2: {result['ATR * 2']:.2f}%, Reason: {result['Reason']}")

    # Calculate and display current risk after final trades
    current_risk = calculate_current_risk(open_orders)
    print(colored(f"Current Risk: ${current_risk:.2f}", 'red'))

    print(colored(f"\n--- Portfolio Size at the End: ${portfolio_size} ---", 'cyan'))
    print(colored(f"\n--- Total Number of Stocks Analyzed: {total_stocks_analyzed} ---", 'cyan'))
    print(colored(f"\n--- Total Possible Number of Trades Made: {total_trades_made} ---", 'cyan'))  # Display the total trades made

if __name__ == "__main__":
    main()

# from utils.api import login_to_robinhood, get_top_movers, fetch_historical_data, load_csv_data, sanitize_ticker_symbols, get_portfolio_size
# from utils.trading import analyze_stock, send_trade_summary
# from utils.trade_state import fetch_open_orders, calculate_current_risk, get_open_trades, TradeState
# from utils.settings import SIMULATED, SIMULATED_PORTFOLIO_SIZE, MAX_DAILY_LOSS, USE_CSV_DATA, USE_NASDAQ_DATA, USE_SP500_DATA, ATR_THRESHOLDS
# from termcolor import colored  # Import termcolor for colored output

# def main():
#     login_to_robinhood()
#     simulated = SIMULATED  # Use setting from settings.py
#     portfolio_size = get_portfolio_size(simulated, simulated_size=SIMULATED_PORTFOLIO_SIZE)
#     max_daily_loss = portfolio_size * MAX_DAILY_LOSS  # Use setting from settings.py
#     current_risk = 0  # Track the current risk as trades are made
    
#     # Boolean options to control the data source
#     use_csv_data = USE_CSV_DATA  # Use setting from settings.py
#     use_nasdaq_data = USE_NASDAQ_DATA  # Use setting from settings.py
#     use_sp500_data = USE_SP500_DATA  # Use setting from settings.py

#     stock_symbols = []

#     if use_csv_data:
#         if use_nasdaq_data and not use_sp500_data:
#             nasdaq_data = load_csv_data('nasdaq100_full.csv', 'nasdaq')
#             nasdaq_data = sanitize_ticker_symbols(nasdaq_data)
#             stock_symbols = nasdaq_data['Ticker'].tolist()
#         elif use_sp500_data and not use_nasdaq_data:
#             sp500_data = load_csv_data('sp500_companies.csv', 'sp500')
#             sp500_data = sanitize_ticker_symbols(sp500_data)
#             stock_symbols = sp500_data['Symbol'].tolist()
#         elif use_nasdaq_data and use_sp500_data:
#             nasdaq_data = load_csv_data('nasdaq100_full.csv', 'nasdaq')
#             nasdaq_data = sanitize_ticker_symbols(nasdaq_data)
#             sp500_data = load_csv_data('sp500_companies.csv', 'sp500')
#             sp500_data = sanitize_ticker_symbols(sp500_data)
#             stock_symbols = nasdaq_data['Ticker'].tolist() + sp500_data['Symbol'].tolist()
#     else:
#         stock_symbols = get_top_movers()

#     results = []
#     total_stocks_analyzed = 0
#     total_trades_made = 0  # Counter for trades made

#     # Fetch open orders and calculate current risk
#     open_orders = fetch_open_orders()
#     current_risk = calculate_current_risk(open_orders)

#     # Analyze all stocks and collect valid trades
#     for stock in stock_symbols:
#         trade_made = analyze_stock(stock, results, portfolio_size, current_risk, atr_thresholds=ATR_THRESHOLDS, simulated=simulated)
        
#         if trade_made:
#             total_trades_made += 1

#             if current_risk > max_daily_loss:
#                 print(colored(f"Daily loss limit exceeded after analyzing {stock}. No more trades will be made, but all stocks will be analyzed.", 'red'))
        
#         total_stocks_analyzed += 1

#     # Fetch and display current open trades
#     openTrades = get_open_trades(open_orders)
#     print(colored("\n--- Open Trades ---", 'magenta'))
#     for trade in openTrades:
#         print(trade)

#     # List all trades that met the criteria
#     print(colored("\n--- All Valid Trade Opportunities ---", 'cyan'))
#     for result in results:
#         if result['Eligible for Trade']:
#             print(colored(f"{result['Stock']}: Trade Amount: ${result['Trade Amount']:.2f}, Shares to Purchase: {result['Shares to Purchase']:.2f} shares, ATR: {result['ATR']:.2f} ({result['ATR Percent']:.2f}%), Reason: {result['Reason']}", 'green'))

#     # Sort results based on ATR Percent in descending order
#     results.sort(key=lambda x: x['ATR Percent'], reverse=True)

#     # Select the top three trades
#     top_trades = [trade for trade in results if trade['Eligible for Trade']][:3]

#     # Send the summary message with open trades info
#     send_trade_summary(top_trades, portfolio_size, current_risk, openTrades)

#     print(colored("\n--- Summary of Top Three Bullish Crossover Trades ---", 'yellow'))
#     for result in top_trades:
#         print(f"{result['Stock']}: {colored('Eligible for Trade:', 'blue')} {result['Eligible for Trade']}, {colored('Trade Made:', 'blue')} {result['Trade Made']}, Trade Amount: ${result['Trade Amount']:.2f}, Shares to Purchase: {result['Shares to Purchase']:.2f} shares, Potential Gain: ${result['Potential Gain']:.2f}, Risk: {result['Risk Percent']:.2f}% (${result['Risk Dollar']:.2f}), ATR: {result['ATR']:.2f} ({result['ATR Percent']:.2f}%), Reason: {result['Reason']}")

#     # Calculate and display current risk after final trades
#     current_risk = calculate_current_risk(open_orders)
#     print(colored(f"Current Risk: ${current_risk:.2f}", 'red'))

#     print(colored(f"\n--- Portfolio Size at the End: ${portfolio_size} ---", 'cyan'))
#     print(colored(f"\n--- Total Number of Stocks Analyzed: {total_stocks_analyzed} ---", 'cyan'))
#     print(colored(f"\n--- Total Possible Number of Trades Made: {total_trades_made} ---", 'cyan'))  # Display the total trades made

# if __name__ == "__main__":
#     main()
