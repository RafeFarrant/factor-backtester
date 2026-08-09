import sys
sys.path.append(".")
import numpy as np
import pandas as pd
from src.data_loader import load_prices
from src.factors import (compute_returns, momentum_score,
                         value_score, quality_score)
from src.backtest import run_backtest, benchmark
from src.drawdown import rolling_start_analysis, blend_returns
import matplotlib.pyplot as plt

prices = load_prices()
returns = compute_returns(prices)

scores = {"Momentum": momentum_score(prices),
          "Value": value_score(prices),
          "Quality": quality_score(prices)}
first = max(sc.dropna(how="all").index[60] for sc in scores.values())

# Factor return streams (net of costs) to feed the retirement engine
net = {name: run_backtest(returns, sc, first)["net"] for name, sc in scores.items()}

# A bond proxy: flat ~3%/yr in monthly terms (v1 simplification, stated as such)
bond_monthly = pd.Series((1.03) ** (1/12) - 1, index=net["Quality"].index)

# --- Allocations to compare ---
allocations = {
    "100% Momentum":        net["Momentum"],
    "100% Quality (low-vol)": net["Quality"],
    "60/40 Quality/Bonds":  blend_returns([net["Quality"], bond_monthly], [60, 40]),
    "Balanced blend":       blend_returns(
        [net["Momentum"], net["Quality"], bond_monthly], [40, 40, 20]),
}

# --- Run the stress test for each allocation ---
print(f"{'Allocation':<26}{'Success':>9}{'Median end £':>15}{'Worst end £':>14}")
print("-" * 64)
results = {}
for name, stream in allocations.items():
    res = rolling_start_analysis(stream, horizon_years=10,
                                 start_pot=500_000, annual_withdrawal=20_000)
    results[name] = res
    print(f"{name:<26}{res['success_rate']*100:>8.0f}%"
          f"{res['median_terminal']:>15,.0f}{res['worst_terminal']:>14,.0f}")

print(f"\n(£500k pot, £20k/yr inflation-adjusted withdrawal = 4% rule, "
      f"20-year horizon, {results['100% Momentum']['n_starts']} historical start dates)")

# --- Fan chart for the two extremes: Momentum vs 60/40 Quality/Bonds ---
fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
for ax, name in zip(axes, ["100% Momentum", "60/40 Quality/Bonds"]):
    res = results[name]
    for path, ok in zip(res["paths"], res["survived"]):
        ax.plot(np.arange(len(path)) / 12, np.array(path) / 1000,
                color=("grey" if ok else "red"), alpha=0.25, linewidth=0.8)
    # median path
    L = min(len(p) for p in res["paths"])
    med = np.median(np.array([p[:L] for p in res["paths"]]), axis=0)
    ax.plot(np.arange(L) / 12, med / 1000, color="black", linewidth=2.2, label="Median")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title(f"{name}\n(success {res['success_rate']*100:.0f}%)")
    ax.set_xlabel("Years into retirement")
    ax.legend()
axes[0].set_ylabel("Pot value (£000s)")
plt.suptitle("Retirement drawdown across every historical start date", fontsize=13)
plt.tight_layout()
plt.savefig("results/drawdown_fan.png", dpi=120)
print("\nSaved fan chart to results/drawdown_fan.png")
plt.show()