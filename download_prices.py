import pandas as pd
import yfinance as yf

tickers = pd.read_csv("data/universe.csv")["ticker"].tolist()
print(f"Downloading {len(tickers)} tickers... this may take a minute or two.")

data = yf.download(tickers, start="2005-01-01", interval="1mo", auto_adjust=True)

prices = data["Close"]
prices.to_parquet("data/prices.parquet")

n_full = prices.notna().all().sum()
n_partial = prices.isna().any().sum()
print(f"Saved price data: {prices.shape[0]} months x {prices.shape[1]} tickers")
print(f"Tickers with full history: {n_full}")
print(f"Tickers with some gaps: {n_partial}")
print("File written to data/prices.parquet")
