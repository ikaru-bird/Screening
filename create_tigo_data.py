import yfinance as yf
import os

# Define the ticker and the path to save the CSV
ticker_symbol = "TIGO"
output_dir = "_files/US"
output_path = os.path.join(output_dir, f"{ticker_symbol}.csv")

# Create the directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

print(f"Fetching data for {ticker_symbol}...")
try:
    # Fetch historical data
    ticker_data = yf.Ticker(ticker_symbol)
    # Get data for a reasonable period, e.g., 5 years
    hist = ticker_data.history(period="5y")

    if hist.empty:
        print(f"No data found for ticker {ticker_symbol}. It might be delisted or invalid.")
    else:
        # Save to CSV
        hist.to_csv(output_path)
        print(f"Successfully saved data for {ticker_symbol} to {output_path}")

except Exception as e:
    print(f"An error occurred: {e}")
