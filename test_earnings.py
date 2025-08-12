import yfinance as yf
from classEarningsInfo import EarningsInfo

def test_tickers():
    tickers = ["TMUS", "NWG"]
    for ticker_str in tickers:
        print(f"--- Testing {ticker_str} ---")
        try:
            ticker_obj = yf.Ticker(ticker_str)

            # The EarningsInfo class fetches data in its constructor.
            ern_info = EarningsInfo(ticker_obj)

            # Call the method we modified.
            summary = ern_info.get_formatted_earnings_summary()

            print(f"Earnings Summary for {ticker_str}:")
            print(summary)
            print("-" * (len(ticker_str) + 25))
            print("\n")

        except Exception as e:
            print(f"An error occurred while testing {ticker_str}: {e}")

if __name__ == "__main__":
    test_tickers()
