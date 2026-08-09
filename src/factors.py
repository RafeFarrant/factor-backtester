import pandas as pd


def compute_returns(prices):
    """Monthly simple returns, one column per ticker."""
    return prices.pct_change()


def momentum_score(prices):
    """12-month return, skipping the most recent month (the '12-minus-1'
    construction). Higher = stronger recent winner."""
    return prices.shift(1) / prices.shift(12) - 1


def value_score(prices):
    """Long-term reversal: negative of trailing 60-month (5yr) return.
    Past long-term losers score high -> the 'value' tilt."""
    return -(prices / prices.shift(60) - 1)


def quality_score(prices):
    """Low-volatility: negative of trailing 36-month return volatility.
    Low-vol (steadier) stocks score high."""
    returns = prices.pct_change()
    return -returns.rolling(36).std()


def form_portfolio(scores, date, quantile=0.2):
    """Return the tickers in the top `quantile` (default top 20%) on `date`."""
    s = scores.loc[date].dropna()
    if len(s) == 0:
        return []
    cutoff = s.quantile(1 - quantile)
    return s[s >= cutoff].index.tolist()