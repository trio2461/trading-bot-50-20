from utils.api import login_to_robinhood, get_top_movers, fetch_historical_data, load_csv_data, sanitize_ticker_symbols, get_portfolio_size
from utils.trading import analyze_stock
from termcolor import colored  # Import termcolor for colored output

def main():
    login_to_robinhood()
    simulated = True
    portfolio_size = get_portfolio_size(simulated)
    daily_loss_limit = 0
    
    # Boolean options to control the data source
    use_csv_data = True  # Set to True to use CSV data; False to use top movers
    use_nasdaq_data = False  # Set to True to use NASDAQ data only
    use_sp500_data = True  # Set to True to use S&P 500 data only

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
    count_3_percent_atr = 0
    total_stocks_analyzed = 0
    total_trades_made = 0  # Counter for trades made

    for stock in stock_symbols:
        trade_made = analyze_stock(stock, results, portfolio_size, daily_loss_limit, simulated=simulated, atr_threshold=0.03)
        if trade_made:
            total_trades_made += 1  # Increment for each successful trade
        if results and results[-1]['ATR Percent'] >= 3:  # Check if results list is not empty
            count_3_percent_atr += 1
        total_stocks_analyzed += 1

    results.sort(key=lambda x: x['ATR Percent'], reverse=True)

    print("\n--- Summary of Bullish Crossovers and Trades ---")
    for result in results:
        if result['Signal'] == "Bullish Crossover":
            print(f"{result['Stock']}: Trade Made: {result['Trade Made']}, Trade Amount: {result['Trade Amount']:.2f} shares, Potential Gain: ${result['Potential Gain']:.2f}, Risk: {result['Risk Percent']:.2f}% (${result['Risk Dollar']:.2f}), ATR: {result['ATR']:.2f} ({result['ATR Percent']:.2f}%), Reason: {result['Reason']}")
    
    print(f"\n--- Portfolio Size at the End: ${portfolio_size} ---")
    print(f"\n--- Number of stocks with ATR >= 3% of stock price: {colored(count_3_percent_atr, 'red')} ---")
    print(f"\n--- Total Number of Stocks Analyzed: {total_stocks_analyzed} ---")
    print(f"\n--- Total Number of Trades Made: {total_trades_made} ---")  # Display the total trades made

if __name__ == "__main__":
    main()
