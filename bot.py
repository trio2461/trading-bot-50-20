# bot.py
from utils.api import get_top_movers, load_csv_data, sanitize_ticker_symbols
from utils.account_data import global_account_data, update_global_account_data
from utils.trading import analyze_stock, send_trade_summary, execute_trade, check_and_execute_sells
from utils.trade_state import calculate_current_risk, get_open_trades
from utils.settings import SIMULATED, SIMULATED_PORTFOLIO_SIZE, MAX_DAILY_LOSS, USE_CSV_DATA, USE_NASDAQ_DATA, USE_SP500_DATA, ATR_THRESHOLDS  
from data_loader import load_stock_symbols  
from termcolor import colored
import robin_stocks.robinhood as r
from tqdm import tqdm

def main():
    update_global_account_data()
    simulated = SIMULATED  
    portfolio_size = SIMULATED_PORTFOLIO_SIZE if simulated else float(global_account_data['portfolio_info']['equity'])  

    max_daily_loss = portfolio_size * MAX_DAILY_LOSS
    open_positions = r.account.get_open_stock_positions()  
    open_trades = get_open_trades(open_positions)  
    current_risk_percent, current_risk_dollar = calculate_current_risk(open_trades, portfolio_size)

    risk_available_for_new_trades = max_daily_loss - current_risk_dollar

    if USE_CSV_DATA:
        stock_symbols = load_stock_symbols()  
    else:
        stock_symbols = get_top_movers()

    with tqdm(stock_symbols, desc="Analyzing stocks", position=0, leave=True, ncols=100) as progress_bar:
        results = []
        total_stocks_analyzed = 0
        total_trades_made = 0

        for stock in stock_symbols:
            progress_bar.set_description(f"Analyzing {stock}")
            eligible_for_trade = analyze_stock(stock, results, portfolio_size, current_risk_percent, atr_thresholds=ATR_THRESHOLDS, simulated=simulated)
            total_stocks_analyzed += 1
            progress_bar.update(1)  

            if not eligible_for_trade:
                tqdm.write(f"{stock} skipped due to ATR percent being less than 3%.")

    print(colored(f"\nInitial Risk (from open positions): {current_risk_percent:.2f}% of Portfolio", 'yellow'))
    print(colored(f"Max Allowed Risk: {MAX_DAILY_LOSS * 100:.2f}% of Portfolio", 'yellow'))
    print(colored(f"Risk Available for New Trades: ${risk_available_for_new_trades:.2f}", 'yellow'))

    print(colored("\n--- Analysis Summary ---", 'yellow'))
    for result in results:
        print(f"{result['Stock']}: {colored('Eligible for Trade:', 'blue')} {result['Eligible for Trade']}, "
              f"ATR Percent: {colored(f'{result['ATR Percent']:.2f}%', 'cyan')}, "
              f"Reason: {result['Reason']}")

    results.sort(key=lambda x: x['ATR Percent'], reverse=True)
    top_trades = [trade for trade in results if trade['Eligible for Trade']][:3]

    for trade in top_trades:
        if current_risk_percent >= MAX_DAILY_LOSS * 100:
            print(colored(f"Daily loss limit exceeded. No more trades will be made.", 'red'))
            break
        elif trade['Risk Dollar'] > risk_available_for_new_trades:
            print(colored(f"Trade for {trade['Stock']} skipped due to insufficient risk allowance.", 'red'))
            continue

        trade_made = execute_trade(trade, portfolio_size, current_risk_percent, simulated)

        if trade_made:
            new_risk_percent = (trade['Risk Dollar'] / portfolio_size) * 100
            current_risk_percent += new_risk_percent
            risk_available_for_new_trades -= trade['Risk Dollar']

            print(f"Updated Risk after trade: {current_risk_percent:.2f}% of Portfolio")
            print(f"Risk Available for New Trades: ${risk_available_for_new_trades:.2f}")

    print(colored(f"\n--- Final Portfolio Size at the End: ${portfolio_size:.2f} ---", 'cyan'))

    print("\n--- Current Positions ---\n")
    positions = global_account_data['positions']
    if positions:
        for symbol, data in positions.items():
            print(f"\nStock: {data['name']}")
            print(f" - Quantity: {data['quantity']} shares")
            print(f" - Current Price: ${data['price']}")
            print(f" - Average Buy Price: ${data['average_buy_price']}")
            print(f" - Equity: ${data['equity']}")
            print(f" - Percent Change: {data['percent_change']}%")
            print(f" - Equity Change: ${data['equity_change']}\n")
    else:
        print("No positions found.")

    send_trade_summary(top_trades, portfolio_size, current_risk_percent, open_trades)

    print(colored("\n--- Summary of Top Three Bullish Crossover Trades ---", 'yellow'))
    for result in top_trades:
        print(f"{result['Stock']}: {colored('Eligible for Trade:', 'blue')} {result['Eligible for Trade']}, {colored('Trade Made:', 'blue')} {result['Trade Made']}, Trade Amount: ${result['Trade Amount']:.2f}, Shares to Purchase: {result['Shares to Purchase']:.2f} shares, Potential Gain: ${result['Potential Gain']:.2f}, Risk: {result['Risk Percent']:.2f}% (${result['Risk Dollar']:.2f}), ATR: {result['ATR']:.2f} ({result['ATR Percent']:.2f}%), ATR * 2: {result['ATR * 2']:.2f}%, Reason: {result['Reason']}")

    print(colored(f"\n--- Portfolio Size at the End: ${portfolio_size:.2f} ---", 'cyan'))
    print(colored(f"\n--- Total Number of Stocks Analyzed: {total_stocks_analyzed} ---", 'cyan'))
    print(colored(f"\n--- Total Possible Number of Trades Made: {total_trades_made} ---", 'cyan'))

    print(colored("\n--- All Possible Trades ---", 'green'))
    for idx, trade in enumerate(results, start=1):
        print(f"{idx}. Stock: {colored(trade['Stock'], 'yellow')}, ATR Percent: {colored(f'{trade['ATR Percent']:.2f}%', 'cyan')}, "
              f"Eligible: {colored(trade['Eligible for Trade'], 'blue')}, Trade Amount: {colored(f'${trade['Trade Amount']:.2f}', 'magenta')}, "
              f"Risk Percent: {colored(f'{trade['Risk Percent']:.2f}%', 'red')}")

    print(colored("\n--- Top Three Trades ---", 'yellow'))
    for idx, trade in enumerate(top_trades, start=1):
        print(f"{idx}. Stock: {colored(trade['Stock'], 'yellow')}, ATR Percent: {colored(f'{trade['ATR Percent']:.2f}%', 'cyan')}, "
              f"Eligible: {colored(trade['Eligible for Trade'], 'blue')}, Trade Amount: {colored(f'${trade['Trade Amount']:.2f}', 'magenta')}, "
              f"Risk Percent: {colored(f'{trade['Risk Percent']:.2f}%', 'red')}")

if __name__ == "__main__":
    main()
