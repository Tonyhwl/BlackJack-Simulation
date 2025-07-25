# Blackjack Betting Strategy Simulation

This project compares two capital allocation strategies in Blackjack — Martingale and Fixed Fractional — using Monte Carlo simulations. The analysis evaluates both strategies based on risk-adjusted returns, ruin probability, and drawdown under realistic 6-deck Blackjack conditions.

## Overview

The goal is to assess the performance and risk of two betting systems by simulating over 100,000 Blackjack hands. The focus is not on optimal play strategy, but on how betting logic impacts long-term outcomes. Players hit until reaching 17 or above, with no splitting or doubling, to isolate betting behavior.

## Strategy Descriptions

- Martingale: Doubles the bet after every loss, resets to base bet after a win or draw. If a required bet exceeds the bankroll, the simulation ends.
- Fixed Fractional: Bets a constant percentage (e.g., 5%) of current bankroll on every hand, regardless of outcomes.

## Simulation Methodology

- Game rules: 6 decks, fixed player/dealer strategy, hit to 17
- 1,000 simulations of 100 games each, for both strategies (100,000 total games per strategy)
- Monte Carlo approach to simulate outcome variance
- Key risk metrics tracked per session and averaged across runs

## Metrics Calculated

- Expected value (EV) per 10-hand session
- Sharpe ratio (mean return divided by standard deviation)
- Ruin probability (sessions where bankroll reaches 0)
- Maximum drawdown
- Average bet size
- Win and loss rates

## Key Results (Averaged Over 10 Batches)

| Metric               | Martingale     | Fixed Fractional |
|----------------------|----------------|------------------|
| EV per 10 hands (£)  | -450           | +275             |
| Sharpe ratio         | -0.051         | +0.073           |
| Ruin probability (%) | 68.1           | 0.0              |
| Max drawdown (%)     | 100            | 95.2             |
| Average bet (£)      | ~1,390         | ~495             |
| Win rate (%)         | ~40.8          | ~40.8            |

These results confirm the inherent risk of Martingale betting. Despite occasional short-term gains, Martingale regularly leads to full bankroll loss. In contrast, Fixed Fractional betting delivers a stable and capital-efficient performance profile, avoiding ruin entirely even under identical game conditions.

## Project Files

- `martingale_blackjack.py`: Simulates Blackjack using Martingale betting
- `fractional_blackjack.py`: Simulates Blackjack using Fixed Fractional betting
- `Blackjack_Betting_Strategy_Analysis.pdf`: Full analysis with charts, session averages, and written conclusions


## Tools and Libraries Used

- Python 3
- numpy
- matplotlib
- pickle 

## Summary

This simulation demonstrates that aggressive recovery systems like Martingale may yield short-term wins but collapse under realistic bankroll constraints. Fixed Fractional betting, though conservative, maintains capital stability and achieves superior risk-adjusted performance.

This project was completed independently to explore stochastic processes, risk modelling, and portfolio theory principles using Python.
