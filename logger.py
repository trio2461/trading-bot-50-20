# logger.py
from termcolor import colored
from datetime import datetime
import json  # Import for JSON pretty printing

def log_initial_risk(current_risk_percent, max_allowed_risk, risk_available_for_new_trades):
    print(colored(f"\nInitial Risk (from open positions): {current_risk_percent:.2f}% of Portfolio", 'yellow'))
    print(colored(f"Max Allowed Risk: {max_allowed_risk:.2f}% of Portfolio", 'yellow'))
    print(colored(f"Risk Available for New Trades: ${risk_available_for_new_trades:.2f}", 'yellow'))

def log_analysis_summary(results):
    print(colored("\n--- Analysis Summary ---", 'yellow'))
    for result in results:
        print(f"{result['Stock']}: {colored('Eligible for Trade:', 'blue')} {result['Eligible for Trade']}, "
              f"ATR Percent: {colored(f'{result['ATR Percent']:.2f}%', 'cyan')}, "
              f"Reason: {result['Reason']}")

def log_trade_execution_skipped(stock, reason):
    print(colored(f"Trade for {stock} skipped due to {reason}.", 'red'))

def log_trade_execution_success(stock, current_risk_percent, risk_available_for_new_trades):
    print(f"Updated Risk after trade: {current_risk_percent:.2f}% of Portfolio")
    print(f"Risk Available for New Trades: ${risk_available_for_new_trades:.2f}")

def log_final_portfolio_size(portfolio_size):
    print(colored(f"\n--- Final Portfolio Size at the End: ${portfolio_size:.2f} ---", 'cyan'))


def log_current_positions(positions):
    print("\n--- Current Positions ---\n")
    if positions:
        # Print the entire dictionary before modifications
        print("Complete positions dictionary before modification:")
        print(json.dumps(positions, indent=4))  # Pretty print the full dictionary with 4-space indentation
        
        # Iterate through positions for individual field printing
        for symbol, data in positions.items():
            # Safely handle parsing of the purchase date
            if 'purchase_date' in data:
                try:
                    days_held = (datetime.now() - datetime.strptime(data['purchase_date'], "%Y-%m-%d")).days
                except ValueError:
                    days_held = 0  # Default to 0 if the date format is unexpected
            else:
                days_held = 0
            
            # Update the global positions dictionary with days_held
            positions[symbol]['days_held'] = days_held

            print(f"{colored('Stock:', 'cyan')} {colored(data['name'], 'yellow')}")
            quantity = float(data['quantity'])
            print(f" - {colored('Quantity:', 'blue')} {colored(f'{quantity:.8f}', 'magenta')} shares")
            price = float(data['price'])
            print(f" - {colored('Current Price:', 'blue')} {colored(f'${price:.2f}', 'green')}")
            print(f" - {colored('Average Buy Price:', 'blue')} {colored(f'${float(data['average_buy_price']):.4f}', 'green')}")
            print(f" - {colored('Equity:', 'blue')} {colored(f'${float(data['equity']):.2f}', 'green')}")
            print(f" - {colored('Percent Change:', 'blue')} {colored(f'{float(data['percent_change']):.2f}%', 'green')}")
            print(f" - {colored('Equity Change:', 'blue')} {colored(f'${float(data['equity_change']):.6f}', 'green')}")
            print(f" - {colored('Days Held:', 'blue')} {colored(f'{days_held}', 'green')} days\n")
        
        # Print the modified dictionary to verify that 'days_held' was added
        print("Complete positions dictionary after modification (with days_held):")
        print(json.dumps(positions, indent=4))  # Pretty print the updated dictionary

    else:
        print("No positions found.")

def log_top_trades(top_trades):
    print(colored("\n--- Summary of Top Three Bullish Crossover Trades ---", 'yellow'))
    for result in top_trades:
        print(f"{result['Stock']}: {colored('Eligible for Trade:', 'blue')} {result['Eligible for Trade']}, {colored('Trade Made:', 'blue')} {result['Trade Made']}, "
              f"Trade Amount: ${result['Trade Amount']:.2f}, Shares to Purchase: {result['Shares to Purchase']:.2f} shares, "
              f"Potential Gain: ${result['Potential Gain']:.2f}, Risk: {result['Risk Percent']:.2f}% (${result['Risk Dollar']:.2f}), "
              f"ATR: {result['ATR']:.2f} ({result['ATR Percent']:.2f}%), ATR * 2: {result['ATR * 2']:.2f}%, Reason: {result['Reason']}")

def log_all_possible_trades(results):
    print(colored("\n--- All Possible Trades ---", 'green'))
    for idx, trade in enumerate(results, start=1):
        print(f"{idx}. Stock: {colored(trade['Stock'], 'yellow')}, ATR Percent: {colored(f'{trade['ATR Percent']:.2f}%', 'cyan')}, "
              f"Eligible: {colored(trade['Eligible for Trade'], 'blue')}, Trade Amount: {colored(f'${trade['Trade Amount']:.2f}', 'magenta')}, "
              f"Risk Percent: {colored(f'{trade['Risk Percent']:.2f}%', 'red')}")

def log_top_three_trades(top_trades):
    print(colored("\n--- Top Three Trades ---", 'yellow'))
    for idx, trade in enumerate(top_trades, start=1):
        print(f"{idx}. Stock: {colored(trade['Stock'], 'yellow')}, ATR Percent: {colored(f'{trade['ATR Percent']:.2f}%', 'cyan')}, "
              f"Eligible: {colored(trade['Eligible for Trade'], 'blue')}, Trade Amount: {colored(f'${trade['Trade Amount']:.2f}', 'magenta')}, "
              f"Risk Percent: {colored(f'{trade['Risk Percent']:.2f}%', 'red')}")