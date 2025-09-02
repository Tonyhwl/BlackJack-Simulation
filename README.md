# Blackjack Betting Simulator (Python)

Compare **Martingale** vs **Fixed-Fractional** as position sizing rules in blackjack. Same rules, same first-hand stake—very different risk profiles.

## What it does
- Runs Monte Carlo over sessions of blackjack hands.
- Plays both strategies under identical rules and initial stake.
- Reports: win/loss, expected return per session, volatility (std), Sharpe, ruin %, drawdown.

## Rules & assumptions
- S17 (dealer stands on all 17), 3:2 player blackjack.
- Naturals resolved before play (push if both).
- Immediate bust ends the hand (no dealer draw after player bust).
- Player logic: basic-lite (stand on hard ≥17; stand on soft ≥19; else hit).
- No splits/surrender; no counting.

## Quick start
```bash
python Fixed_Fractional.py
python Martingale.py
