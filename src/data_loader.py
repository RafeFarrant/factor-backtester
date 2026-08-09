import os
import pandas as pd
import yfinance as yf

DATA_DIR = "data"
PRICES_PATH = os.path.join(DATA_DIR, "prices.parquet")
UNIVERSE_PATH = os.path.join(DATA_DIR, "universe.csv")


def load_universe():
    """Return the list of tickers from the saved universe file."""
    return pd.read_csv(UNIVERSE_PATH)["ticker"].tolist()


def download_prices(start="2005-01-01"):
    """Download monthly adjusted prices and cache them to disk."""
    tickers = load_universe()
    print(f"Downloading {len(tickers)} tickers...")
    data = yf.download(tickers, start=start, interval="1mo", auto_adjust=True)
    prices = data["Close"]
    os.makedirs(DATA_DIR, exist_ok=True)
    prices.to_parquet(PRICES_PATH)
    return prices


def load_prices():
    """Load prices from cache if present, otherwise download and cache."""
    if os.path.exists(PRICES_PATH):
        return pd.read_parquet(PRICES_PATH)
    return download_prices()