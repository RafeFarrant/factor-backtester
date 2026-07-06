# Factor Backtester & Retirement Drawdown Stress-Tester

A Python tool that backtests Value, Momentum, and Quality factor strategies across ~20 years of S&P 500 data, then stress-tests retirement withdrawal plans against every historical return sequence to measure how different allocations hold up for a client drawing down their pot.

## Motivation

This project extends quantitative equity analysis I originally built and presented to the CEO and CIO during a placement at Lloyds Wealth, rebuilding it from scratch as an open-source tool and adding a retirement drawdown module to explore sequence-of-returns risk.

## Planned outputs

- A backtesting engine reporting Sharpe ratio, max drawdown, and regime-by-regime performance net of transaction costs
- A retirement drawdown simulator with rolling-start historical stress-testing
- An accompanying presentation walking through the methodology and findings

*Work in progress — results and full documentation to follow.*
