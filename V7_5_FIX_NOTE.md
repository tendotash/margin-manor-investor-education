# Margin Manor V7.5 — Comprehensive Reads + Macro Data Fix

## Timeframe reads
The member engine no longer presents only Bullish / Bearish / Neutral to the member.
The three-way bias remains internally for weighting, while each timeframe now receives
a richer composite phase read such as:

- Strong Bullish Alignment
- Bullish Continuation
- Bullish Structure · Bearish Pullback
- Bearish Structure · Bullish Recovery
- Bullish Expansion · Developing
- Bearish Expansion · Developing
- Bullish Trend · Consolidating
- Bearish Trend · Consolidating
- Two-Way Transition
- Balanced / Range
- Extended conditions when RSI and ATR-distance show stretch

The table also gives Structure, Trend, Momentum, and a separate Condition column.

## Driver reads
Drivers no longer show only Rising / Falling / Neutral.
They can now show:

- Strongly Rising · Momentum Confirmed
- Rising · Momentum Accelerating
- Rising · Trend Intact
- Rising · Momentum Cooling
- Reversing Higher
- Stable / Range-Bound
- Reversing Lower / Pullback
- Falling · Momentum Cooling
- Falling · Trend Intact
- Falling · Momentum Accelerating
- Strongly Falling · Momentum Confirmed

Driver direction is translated separately into:
Strong / Moderate / Mild Tailwind, Mixed / Neutral, or Strong / Moderate / Mild Headwind.

## US Real Yield / US 2Y / 10Y Breakeven fix
The key Treasury-derived macro series now use three official-source layers:

1. Optional FRED API if `FRED_API_KEY` exists in Streamlit Secrets.
2. FRED public CSV download.
3. Official U.S. Treasury XML fallback.

Fallback mappings:
- DGS2 -> Treasury 2Y daily par yield
- DFII10 -> Treasury 10Y daily real par yield
- T10YIE -> derived 10Y nominal Treasury yield minus 10Y real Treasury yield

No FRED API key is required for the Treasury fallback.

## Important
Yahoo/yfinance remains a development market-price feed. Use a properly licensed
commercial market-data provider before selling or redistributing live market data.
