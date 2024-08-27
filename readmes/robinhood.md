cmmd + shift + v to view

### README: **Using `robin_stocks` for Automated Trading on Robinhood**

This README will guide you through setting up and using the `robin_stocks` library to interact with Robinhood's API for automated trading. The focus will be on performing essential tasks like logging in, placing market orders, and checking your portfolio.

---

### **1. Installation**

First, you need to install the `robin_stocks` library. You can do this using pip:

```bash
pip install robin_stocks
```

---

### **2. Importing the Library**

Once installed, you can import `robin_stocks` in your Python script:

```python
import robin_stocks.robinhood as r
```

---

### **3. Logging in to Robinhood**

Before you can execute any trades, you must log in to your Robinhood account. You can log in using your username and password, or with a two-factor authentication (2FA) code if you have it enabled.

```python
# Basic login
r.login(username="your_username", password="your_password")

# Login with 2FA (if enabled)
r.login(username="your_username", password="your_password", mfa_code="your_2fa_code")
```

**Security Note**: It's advisable to store your credentials securely and not hard-code them in your script.

---

### **4. Fetching Account Information**

You can fetch your account information to check your portfolio balance, available buying power, and more.

```python
# Get basic account information
account_info = r.profiles.load_account_profile()
print(account_info)

# Get portfolio information
portfolio = r.profiles.load_portfolio_profile()
print(portfolio)
```

---

### **5. Fetching Market Data**

You can fetch market data, such as stock prices, historical data, and other relevant information.

```python
# Get the current price of a stock
stock_price = r.stocks.get_latest_price("AAPL")[0]
print(f"Current price of AAPL: {stock_price}")

# Get historical data
historical_data = r.stocks.get_stock_historicals("AAPL", interval="day", span="week")
print(historical_data)
```

---

### **6. Placing Trades**

Placing a market order is straightforward. You can specify the stock symbol and the quantity of shares you wish to buy or sell.

```python
# Place a market buy order
order = r.orders.order_buy_market("AAPL", quantity=1)
print(order)

# Place a market sell order
order = r.orders.order_sell_market("AAPL", quantity=1)
print(order)
```

**Parameters**:

-   **symbol**: The ticker symbol of the stock (e.g., "AAPL" for Apple).
-   **quantity**: The number of shares you want to buy or sell.

---

### **7. Checking Order Status**

You can check the status of your orders to ensure they were executed correctly.

```python
# Get all open orders
open_orders = r.orders.get_all_open_stock_orders()
print(open_orders)

# Get details of a specific order by its ID
order_details = r.orders.get_stock_order_info("order_id")
print(order_details)
```

---

### **8. Logging Out**

It's good practice to log out once your script has completed its tasks.

```python
r.logout()
```

---

### **9. Example Workflow**

Here’s a simple example workflow that logs in, checks your buying power, buys 1 share of a stock, and logs out.

```python
import robin_stocks.robinhood as r

def main():
    # Login
    r.login(username="your_username", password="your_password", mfa_code="your_2fa_code")

    # Check buying power
    account_info = r.profiles.load_account_profile()
    print(f"Buying Power: {account_info['buying_power']}")

    # Buy 1 share of AAPL
    order = r.orders.order_buy_market("AAPL", quantity=1)
    print("Order placed:", order)

    # Logout
    r.logout()

if __name__ == "__main__":
    main()
```

---

### **10. Additional Resources**

For more detailed documentation and advanced features, refer to the official [robin_stocks GitHub repository](https://github.com/jmfernandes/robin_stocks).

---

### **11. Best Practices and Security**

-   **Two-Factor Authentication**: Always enable 2FA on your Robinhood account for added security.
-   **Environment Variables**: Store your credentials as environment variables or use a secure credentials manager.
-   **Error Handling**: Implement robust error handling, especially when placing trades to avoid unintended actions.
-   **Simulation Mode**: Always test your scripts thoroughly in a simulated environment before going live.

---

This README should provide you with the foundational knowledge needed to start automating your trades on Robinhood using the `robin_stocks` library. Always ensure that your scripts are secure and thoroughly tested before executing live trades.
