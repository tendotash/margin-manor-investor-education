# V7.3 — Persistent Member Navigation Fix

This build fixes the Streamlit rerun bug in V7.2.

## Problem fixed

After member login, Member Live Insight Engine opened correctly. But changing a
selectbox, toggle, trading style, asset, session, or pressing Run Live Analysis
caused Streamlit to rerun `app.py`. V7.2 reconstructed the current page from
sidebar radio defaults, so the app left the member engine.

## V7.3 behavior

- Login opens Member Live Insight Engine.
- Selecting XAUUSD / EURUSD / NQ / ES etc. stays on Member Live Insight Engine.
- Changing Trading Style stays on the member page.
- Changing Session stays on the member page.
- Manual Override stays on the member page.
- Run Live Analysis stays on the member page.
- Any other Streamlit widget rerun stays on the current page.
- Explicit sidebar navigation still changes pages normally.
- Sign Out returns to Home.

Only navigation/session handling changed. Supabase membership logic and the
Live Insight analysis model are otherwise preserved from V7.2.
