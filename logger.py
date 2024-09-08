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
        for symbol, data in positions.items():
            # Check if purchase_date is available, otherwise use created_at
            purchase_date_str = data.get('purchase_date') or data.get('created_at', None)
            print(f"Debug: Purchase date for {symbol}: {purchase_date_str}")

            if purchase_date_str:
                try:
                    # Parse the purchase date (or created_at)
                    purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                    days_held = (datetime.now() - purchase_date).days
                except ValueError:
                    print(f"Error parsing purchase date for {symbol}, setting days held to 0")
                    days_held = 0
            else:
                print(f"No purchase date or created_at for {symbol}, setting days held to 0")
                days_held = 0

            # Update days held in the global data
            positions[symbol]['days_held'] = days_held
            created_at = data.get('created_at', 'N/A')
            
            print(f"Stock: {colored(data['name'], 'yellow')}")
            print(f" - Days Held: {colored(f'{days_held}', 'green')} days")
            print(f" - Created At: {colored(f'{created_at}', 'green')}\n")
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