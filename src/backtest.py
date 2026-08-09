import numpy as np
import pandas as pd


# ---------- performance metrics ----------

def cagr(r):
    """Compound annual growth rate from monthly returns."""
    r = r.dropna()
    return (1 + r).prod() ** (12 / len(r)) - 1


def vol(r):
    """Annualised volatility from monthly returns."""
    return r.dropna().std() * np.sqrt(12)


def sharpe(r, rf=0.02):
    """Annualised Sharpe ratio (rf = annual risk-free rate)."""
    v = vol(r)
    return (cagr(r) - rf) / v if v > 0 else np.nan


def max_drawdown(r):
    """Largest peak-to-trough loss of the cumulative wealth curve."""
    wealth = (1 + r.dropna()).cumprod()
    peak = wealth.cummax()
    return ((wealth - peak) / peak).min()


# ---------- the backtest loop ----------

def run_backtest(returns, scores, start, quantile=0.2, cost_per_trade=0.001):
    """
    Walk forward month by month. On each date t, rank stocks by `scores`,
    hold the top `quantile` (equal-weighted), earn their return from t to t+1.
    Returns a DataFrame with gross and net (after cost) monthly returns.
    """
    dates = returns.loc[start:].index
    prev_holdings = set()
    gross, net, idx = [], [], []

    for i in range(len(dates) - 1):
        t, t_next = dates[i], dates[i + 1]

        s = scores.loc[t].dropna()
        if len(s) < 20:
            continue
        cutoff = s.quantile(1 - quantile)
        holdings = set(s[s >= cutoff].index)

        # return earned t -> t+1 (equal weight, NaN-safe mean)
        g = returns.loc[t_next, list(holdings)].mean()

        # turnover = fraction of the book replaced this month
        if prev_holdings:
            turnover = len(holdings - prev_holdings) / len(holdings)
        else:
            turnover = 1.0  # first month: buy the whole book
        n = g - turnover * cost_per_trade

        gross.append(g); net.append(n); idx.append(t_next)
        prev_holdings = holdings

    return pd.DataFrame({"gross": gross, "net": net}, index=idx)


def benchmark(returns, start):
    """Equal-weighted return of the whole available universe each month."""
    return returns.loc[start:].mean(axis=1)


def metrics_table(series_dict, rf=0.02):
    """Build a tidy metrics table from a dict of {name: monthly return series}."""
    rows = {}
    for name, r in series_dict.items():
        rows[name] = {
            "CAGR %":   round(cagr(r) * 100, 1),
            "Vol %":    round(vol(r) * 100, 1),
            "Sharpe":   round(sharpe(r, rf), 2),
            "MaxDD %":  round(max_drawdown(r) * 100, 1),
        }
    return pd.DataFrame(rows).T