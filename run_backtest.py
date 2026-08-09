import sys
sys.path.append(".")
import pandas as pd
from src.data_loader import load_prices
from src.factors import (compute_returns, momentum_score,
                         value_score, quality_score)
from src.backtest import run_backtest, benchmark, metrics_table
import matplotlib.pyplot as plt

prices = load_prices()
returns = compute_returns(prices)

scores = {
    "Momentum": momentum_score(prices),
    "Value":    value_score(prices),
    "Quality":  quality_score(prices),
}

# Common start: first date where all three factors have enough data (~2010)
first_dates = [sc.dropna(how="all").index[60] for sc in scores.values()]
start = max(first_dates)
print(f"Backtest start (all factors available): {start.date()}\n")

# Run each factor; collect gross and net streams
gross_streams, net_streams = {}, {}
for name, sc in scores.items():
    bt = run_backtest(returns, sc, start)
    gross_streams[name] = bt["gross"]
    net_streams[name] = bt["net"]

bench = benchmark(returns, start)

# ---- Metrics tables ----
print("=== GROSS (before costs) ===")
print(metrics_table({**gross_streams, "Benchmark (EW)": bench}).to_string())
print("\n=== NET (after 0.1%/trade costs) ===")
print(metrics_table({**net_streams, "Benchmark (EW)": bench}).to_string())

# ---- Regime breakdown (net, CAGR %) ----
from src.backtest import cagr
regimes = {
    "2010-2021 bull": ("2010-01-01", "2021-12-31"),
    "2022 rate shock": ("2022-01-01", "2022-12-31"),
    "2023-present":    ("2023-01-01", "2027-01-01"),
}
print("\n=== NET CAGR % by regime ===")
reg_rows = {}
for name, r in net_streams.items():
    reg_rows[name] = {rn: round(cagr(r.loc[a:b]) * 100, 1)
                      for rn, (a, b) in regimes.items()}
reg_rows["Benchmark"] = {rn: round(cagr(bench.loc[a:b]) * 100, 1)
                         for rn, (a, b) in regimes.items()}
print(pd.DataFrame(reg_rows).T.to_string())

# ---- Headline chart: cumulative growth of £1, net of costs, log scale ----
plt.figure(figsize=(11, 6))
for name, r in net_streams.items():
    (1 + r).cumprod().plot(label=name, linewidth=1.6)
(1 + bench).cumprod().plot(label="Benchmark (EW)", linewidth=1.4,
                           linestyle="--", color="grey")
plt.yscale("log")
plt.title("Growth of £1 by factor strategy (net of costs, log scale)")
plt.ylabel("Cumulative value (£, log)")
plt.legend()
plt.tight_layout()
plt.savefig("results/cumulative_returns.png", dpi=120)
print("\nSaved chart to results/cumulative_returns.png")
plt.show()