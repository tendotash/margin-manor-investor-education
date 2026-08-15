# Margin Manor V7.4 — Resilient Market Data

V7.4 addresses the "development market-data provider did not return enough data"
error seen on the hosted Member Live Insight Engine.

Changes:
- Direct Yahoo chart endpoint added before yfinance.
- yfinance remains as a fallback.
- 5-minute history expanded to 60 days.
- 1-minute history expanded to 7 days.
- If M1 alone fails, a clearly labelled 2-minute proxy can be used in development.
- Missing low-weight timeframes no longer kill the entire analysis.
- Timeframe weights are renormalized across actually available data.
- Data Coverage is displayed in the analysis header.
- If the feed still fails, a diagnostic table shows bar counts, source, and latest
  timestamp for every timeframe.
- Retry Market Data clears the Streamlit data cache and retries.
- Supabase logout remains the only member logout path.

Important:
This remains a development/personal-use market-data adapter. Before monetizing or
redistributing member market data, replace Yahoo with a provider whose commercial
licence covers the intended use.
