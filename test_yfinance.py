import yfinance as yf

print("Testing yfinance for META...")
try:
    ticker = yf.Ticker("META")
    info = ticker.info
    print("Info fetched successfully.")
    # print(info)

    income_stmt = ticker.income_stmt
    print("Income statement fetched successfully.")
    # print(income_stmt)

    print("Test complete.")
except Exception as e:
    print(f"An error occurred: {e}")
