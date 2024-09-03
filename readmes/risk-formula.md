Here's a sample README that explains how the trading bot's calculations and logic work, including the method for adjusting trade amounts based on different ATR (Average True Range) levels.

---

# Trading Bot README

## Overview

This trading bot is designed to manage risk effectively by adjusting trade amounts based on the Average True Range (ATR) of stocks. The bot uses a simple yet robust strategy to ensure that each trade carries a consistent level of risk, specifically 2% of the total portfolio size. This document explains the logic behind the calculations, the trading strategy, and how the bot operates.

## Key Concepts

### Average True Range (ATR)

ATR is a measure of a stock's volatility. It represents the average range of price movement for a given stock over a specific period. In this bot, the ATR is used to determine the trade amount based on the stock's volatility.

### 2x ATR

The bot uses twice the ATR value (2x ATR) to determine the expected move in the stock price. This value is crucial in calculating the trade amount to ensure that the potential loss from a 2x ATR move equals 2% of the portfolio.

### Portfolio Risk Management

The bot is configured to ensure that the potential loss on any given trade is limited to 2% of the total portfolio. This is achieved by adjusting the trade amount based on the stock's ATR.

## Calculation of Trade Amount

The bot supports three different ATR levels—3%, 4%, and 5%—and adjusts the trade amount accordingly. Here's how it works:

1. **5% ATR:**

    - **2x ATR**: This is 10%.
    - **Trade Amount Calculation**: The trade amount is calculated so that a 10% move in the stock price results in a 2% portfolio loss.
      \[
      \text{Trade Amount} = \frac{0.02 \times \text{Portfolio Size}}{0.10}
      \]
    - For a $10,000 portfolio:
      \[
      \text{Trade Amount} = \frac{200}{0.10} = 2000 \text{ dollars}
      \]

2. **4% ATR:**

    - **2x ATR**: This is 8%.
    - **Trade Amount Calculation**: The trade amount is calculated so that an 8% move in the stock price results in a 2% portfolio loss.
      \[
      \text{Trade Amount} = \frac{0.02 \times \text{Portfolio Size}}{0.08}
      \]
    - For a $10,000 portfolio:
      \[
      \text{Trade Amount} = \frac{200}{0.08} = 2500 \text{ dollars}
      \]

3. **3% ATR:**
    - **2x ATR**: This is 6%.
    - **Trade Amount Calculation**: The trade amount is calculated so that a 6% move in the stock price results in a 2% portfolio loss.
      \[
      \text{Trade Amount} = \frac{0.02 \times \text{Portfolio Size}}{0.06}
      \]
    - For a $10,000 portfolio:
      \[
      \text{Trade Amount} = \frac{200}{0.06} = 3333 \text{ dollars}
      \]

## How the Bot Works

1. **Data Source**: The bot can pull stock data from a CSV file or use top movers from a specific market index (e.g., NASDAQ or S&P 500).

2. **Analysis**: For each stock, the bot:

    - Fetches historical data.
    - Calculates the ATR and ATR Percent.
    - Detects crossover signals using moving averages.
    - Checks if the ATR meets the threshold (typically 3% or higher).
    - Adjusts the trade amount based on the ATR Percent.

3. **Trading Decision**:

    - If the bot detects a bullish crossover and the ATR meets the required threshold, it determines the number of shares to buy.
    - The bot then executes a trade or simulates it if in simulated mode.

4. **Risk Management**:
    - The bot ensures that the total risk per trade does not exceed 2% of the portfolio.
    - It also ensures that the cumulative risk does not exceed 6% of the portfolio.

## Configuration

-   **Simulation Mode**: The bot can run in simulation mode, where trades are calculated but not executed.
-   **Data Source**: Users can configure the bot to use different data sources (CSV files or market indices).
-   **ATR Threshold**: The minimum ATR percent required for a stock to be considered for trading.

## Execution

To run the bot, simply execute the `bot.py` script. Ensure that all required dependencies are installed, and the configuration is set correctly.

```bash
python3 bot.py
```

## Conclusion

This trading bot is a powerful tool for managing trades with a consistent risk level. By adjusting trade amounts based on the ATR, it ensures that each trade carries the same level of risk, regardless of the stock's volatility. The bot is designed to be flexible, allowing users to configure it according to their trading strategies and risk tolerance.

---

This README provides a comprehensive overview of how the trading bot operates and the logic behind its calculations. You can download this README as a file if needed.
