# If you want to ensure that market orders are being placed for both full and fractional shares, you can simplify the code to make sure that market orders are being used regardless of the share quantity, while handling fractional orders appropriately. Here’s how you can update the close_trade() function to make sure that market orders are always used, even for fractional shares:
#
# Updated close_trade() Function:

def close_trade(symbol, quantity, sale_price, sale_type=None):
    try:
        # Use market order for fractional or full shares
        if quantity < 1:
            print(f"Closing fractional position for {symbol} using market order.")
            order = r.orders.order_sell_fractional_by_quantity(
                symbol=symbol,
                quantity=quantity,
                timeInForce='gfd',  # Good For Day (for market hours)
                extendedHours=False  # Fractional orders may not work in extended hours
            )
        else:
            print(f"Closing full share position for {symbol} using market order.")
            order = r.orders.order_sell_market(
                symbol=symbol,
                quantity=quantity,
                timeInForce='gfd'  # Good For Day
            )

        if order and 'id' in order:
            print(f"Trade {symbol} closed successfully.")
            current_price = float(global_account_data['positions'][symbol].get('price', 0))
            purchase_price = float(global_account_data['positions'][symbol].get('average_buy_price', 0))
            profit = current_price > purchase_price
            add_sale_to_global_data(symbol, profit, current_price, sale_type)
        else:
            print(f"Failed to close trade for {symbol}. Response: {order}")
    except Exception as e:
        print(f"Exception occurred while closing trade: {e}")

#
#
# Key Points:
#
# 	1.	order_sell_fractional_by_quantity() for fractional shares: This ensures that fractional shares are closed using a market order. The key here is to ensure that you’re using the correct function for fractional shares.
# 	2.	order_sell_market() for full shares: Full shares are sold with a simple market order. This is standard for Robinhood API.
# 	3.	Ensure timeInForce is gfd: gfd (Good For Day) is used for both fractional and full shares to ensure that orders are executed during market hours.
# 	4.	Check if fractional orders fail in extended hours: The extendedHours=False flag ensures that you’re not placing fractional orders during extended trading hours, as Robinhood may not support that.
#





Yes, your proposed changes are absolutely feasible and make a lot of sense for organizing backtesting results and making the bot more modular. Here's how we can approach it step by step:

### 1. **Introducing Backtest Strategies as a Configurable List**:
You want the ability to switch between different backtesting strategies (e.g., MA cross, EMA cross, resistance, etc.). This can be done by creating a list or dictionary of strategies that the bot can iterate through. This list can include flags or values for turning on/off indicators like RSI, ATR, and choosing the strategy type.

#### Example of Strategy Configuration:
```python
# Add this to `config.py` for dynamic strategy selection
BACKTEST_STRATEGIES = [
    {'name': 'MA_Cross', 'use_ema': False, 'use_rsi': True, 'use_atr': True},
    {'name': 'EMA_Cross', 'use_ema': True, 'use_rsi': True, 'use_atr': True},
    {'name': 'Resistance', 'use_ema': False, 'use_rsi': False, 'use_atr': True}
]
```

This way, you can switch between strategies by modifying or selecting from this list. Each strategy has parameters to control whether EMA/MA, RSI, or ATR is used.

### 2. **Updating the Backtest Function to Handle Different Strategies**:
We can modify the `run_backtest()` function to adapt to different strategies based on the configuration.

#### Updated `run_backtest()`:
```python
def run_backtest(instrument, data, candle_limit=None, strategy=None):
    trades = []
    position = None
    balance = INITIAL_BALANCE
    daily_loss = 0
    max_daily_loss = 0.06
    trade_loss_limit = 0.005
    current_date = None
    total_profit = 0
    total_loss = 0
    num_trades = 0
    profit_trades = 0
    loss_trades = 0

    # Choose strategy and apply indicators accordingly
    if strategy['use_ema']:
        data = add_moving_averages(data, use_ema=True)
    else:
        data = add_moving_averages(data, use_ema=False)

    if strategy['use_rsi']:
        data = add_rsi(data)

    if strategy['use_atr']:
        data = add_atr(data)

    # Set the limit for the number of candles (default is all candles if not specified)
    candle_count = len(data)
    if candle_limit is not None:
        candle_count = min(candle_limit, len(data))

    start_date = pd.to_datetime(data['time'].iloc[200])  # Start after MA calculations
    end_date = pd.to_datetime(data['time'].iloc[candle_count - 1])  # Last candle within the limit

    print(f"Backtest Start Date: {start_date}")
    print(f"Backtest End Date: {end_date}")

    # Backtesting logic here (same as your original logic)...

    return trades
```

### 3. **Directory Structure and Dynamic Naming**:
You want to organize backtest results into subdirectories based on the strategy used. We can dynamically create these directories and save the results accordingly.

#### Update the Directory Structure:
```python
def save_results(instrument, trades, output_base_dir, strategy):
    current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    strategy_dir = os.path.join(output_base_dir, strategy['name'])  # Create subdirectory based on strategy
    instrument_dir = os.path.join(strategy_dir, instrument)

    if not os.path.exists(instrument_dir):
        os.makedirs(instrument_dir)

    # Save results
    results_filename = f'{instrument_dir}/{instrument}_backtest_results_{strategy["name"]}_{current_time}.csv'
    trades_df = pd.DataFrame(trades)  # Assuming trades is a list of dictionaries
    trades_df.to_csv(results_filename, index=False)
    print(f"Backtest results for {instrument} ({strategy['name']}) saved in {results_filename}.")
```

### 4. **Adding Subdirectories Based on the Strategy**:
You mentioned that the results need to be placed in specific subdirectories like `backtesting_results/MA/` or `backtesting_results/Support_Resistance/`. This will be handled by the `save_results()` function, as shown above, where the strategy name will dictate the subdirectory.

### 5. **Testing and Final Adjustments**:
You can loop over different strategies to perform backtesting based on the configurations.

#### Example of Running Multiple Strategies:
```python
def backtest_instruments(input_dir, output_base_dir, pair=None):
    # Iterate through each strategy in the BACKTEST_STRATEGIES
    for strategy in BACKTEST_STRATEGIES:
        print(f"Running backtest for strategy: {strategy['name']}")

        if pair:
            filepath = os.path.join(input_dir, f"{pair}.csv")
            if os.path.exists(filepath):
                df = pd.read_csv(filepath)
                df = filter_data_by_year_and_month(df, START_YEAR, START_MONTH)
                trades = run_backtest(pair, df, candle_limit=CANDLE_LIMIT, strategy=strategy)
                save_results(pair, trades, output_base_dir, strategy)
            else:
                print(f"Error: The pair '{pair}' does not exist in the dataset.")
        else:
            # If no pair is specified, backtest all instruments
            for file in os.listdir(input_dir):
                if file.endswith(".csv"):
                    instrument = file.split(".")[0]
                    filepath = os.path.join(input_dir, file)
                    df = pd.read_csv(filepath)
                    df = filter_data_by_year_and_month(df, START_YEAR, START_MONTH)
                    trades = run_backtest(instrument, df, candle_limit=CANDLE_LIMIT, strategy=strategy)
                    save_results(instrument, trades, output_base_dir, strategy)
```

### **Summary**:
- **Dynamic strategy selection**: Strategies are stored in `BACKTEST_STRATEGIES` with parameters for MA, EMA, RSI, and ATR.
- **Modular backtest function**: The `run_backtest()` function handles different strategies based on the configuration.
- **Dynamic directory and file naming**: Subdirectories are created based on the strategy type, and file names are descriptive of the strategy and instrument.

This approach will keep your bot modular, organized, and scalable for future backtesting strategies. Let me know if you need any further refinements or clarifications!
