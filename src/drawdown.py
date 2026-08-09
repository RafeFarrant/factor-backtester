import numpy as np
import pandas as pd


def simulate_path(monthly_returns, start_pot=500_000,
                  annual_withdrawal=20_000, inflation=0.025):
    """
    Run one retirement path: start with `start_pot`, withdraw monthly
    (inflation-adjusted), earn `monthly_returns` each month.
    Returns (path_of_pot_values, survived_bool).
    """
    pot = start_pot
    monthly_wd = annual_withdrawal / 12
    path = []
    for r in monthly_returns:
        pot = pot * (1 + r) - monthly_wd
        monthly_wd *= (1 + inflation) ** (1 / 12)
        path.append(pot)
        if pot <= 0:
            return path, False
    return path, True


def rolling_start_analysis(returns, horizon_years=20, **kwargs):
    """
    Run `simulate_path` from every possible starting month that leaves a full
    `horizon_years` window. Returns a dict of summary stats + the raw paths.
    """
    horizon = horizon_years * 12
    r = returns.dropna().values
    n_starts = len(r) - horizon + 1
    if n_starts < 1:
        raise ValueError(f"Need {horizon} months; only have {len(r)}.")

    paths, survived, terminal = [], [], []
    for i in range(n_starts):
        window = r[i:i + horizon]
        path, ok = simulate_path(window, **kwargs)
        paths.append(path)
        survived.append(ok)
        terminal.append(path[-1] if ok else 0.0)

    return {
        "n_starts": n_starts,
        "success_rate": np.mean(survived),
        "median_terminal": np.median(terminal),
        "worst_terminal": np.min(terminal),
        "paths": paths,
        "survived": survived,
    }


def blend_returns(streams, weights):
    """Weighted blend of several monthly return series (auto-aligned)."""
    df = pd.concat(streams, axis=1).dropna()
    w = np.array(weights) / np.sum(weights)
    return (df * w).sum(axis=1)