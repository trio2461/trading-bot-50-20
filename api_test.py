import robin_stocks.robinhood as r
import os
from dotenv import load_dotenv

# Load environment variables (ROBINHOOD_USERNAME and ROBINHOOD_PASSWORD should be in your .env file)
load_dotenv()

# def login_to_robinhood():
#     username = os.getenv('ROBINHOOD_USERNAME')
#     password = os.getenv('ROBINHOOD_PASSWORD')
#     # theres an extra slash in the password to escape the other slash
#     if not username or not password:
#         print("Username or password not found in environment variables.")
#         return
    
#     try:
#         # Attempt to login with MFA
#         print(f"Attempting to log in with Username: {username}")
#         mfa_code = input("Enter MFA code (if you received it, otherwise press Enter to skip): ").strip()
        
#         # Login with or without MFA code based on user input
#         if mfa_code:
#             login_data = r.authentication.login(username=username, password=password, mfa_code=mfa_code)
#         else:
#             login_data = r.authentication.login(username=username, password=password)

#         print("Login successful!")
#         print(login_data)  # To check the response
#         return login_data

#     except Exception as e:
#         print(f"Login failed: {e}")

def logout_from_robinhood():
    """Logout from Robinhood and clear the saved session file."""
    r.authentication.logout()
    if os.path.exists(PICKLE_NAME):
        os.remove(PICKLE_NAME)
    print("Logged out and session file removed.")

if __name__ == "__main__":
    # login_to_robinhood()
    logout_from_robinhood()