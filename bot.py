# bot.py
from utils.api import get_top_movers, load_csv_data, sanitize_ticker_symbols
from utils.account_data import global_account_data, update_global_account_data
from utils.trading import analyze_stock, send_trade_summary, execute_trade
from utils.trade_state import calculate_current_risk, get_open_trades
from utils.settings import SIMULATED, SIMULATED_PORTFOLIO_SIZE, MAX_DAILY_LOSS, USE_CSV_DATA, ATR_THRESHOLDS  
from data_loader import load_stock_symbols  
import robin_stocks.robinhood as r
from tqdm import tqdm
import logger  # importing the logger file
import json

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

    logger.log_initial_risk(current_risk_percent, MAX_DAILY_LOSS * 100, risk_available_for_new_trades)

    logger.log_analysis_summary(results)

    results.sort(key=lambda x: x['ATR Percent'], reverse=True)
    top_trades = [trade for trade in results if trade['Eligible for Trade']][:3]

    for trade in top_trades:
        if current_risk_percent >= MAX_DAILY_LOSS * 100:
            logger.log_trade_execution_skipped(trade['Stock'], "exceeding daily loss limit")
            break
        elif trade['Risk Dollar'] > risk_available_for_new_trades:
            logger.log_trade_execution_skipped(trade['Stock'], "insufficient risk allowance")
            continue

        trade_made = execute_trade(trade, portfolio_size, current_risk_percent, simulated)

        if trade_made:
            new_risk_percent = (trade['Risk Dollar'] / portfolio_size) * 100
            current_risk_percent += new_risk_percent
            risk_available_for_new_trades -= trade['Risk Dollar']

            logger.log_trade_execution_success(trade['Stock'], current_risk_percent, risk_available_for_new_trades)

    logger.log_final_portfolio_size(portfolio_size)
    logger.log_current_positions(global_account_data['positions'])
    
    send_trade_summary(top_trades, portfolio_size, current_risk_percent, open_trades)

    logger.log_top_trades(top_trades)
    logger.log_all_possible_trades(results)
    logger.log_top_three_trades(top_trades)

    # Print global_account_data at the end of bot.py
    # print("\n--- Global Account Data at the End ---\n")
    # print(json.dumps(global_account_data, indent=4))  # Pretty print the full global_account_data dictionary

if __name__ == "__main__":
    main()