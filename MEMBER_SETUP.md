# Margin Manor V7 Member Engine Setup

## Local owner preview

Create `.streamlit/secrets.toml` locally:

```toml
PREMIUM_PREVIEW = true
member_emails = ["your-email@example.com"]
```

Do not commit `secrets.toml` to GitHub.

## Production member login

Use Streamlit OIDC and whitelist approved member emails:

```toml
PREMIUM_PREVIEW = false
member_emails = [
  "member1@example.com",
  "member2@example.com"
]

[auth]
redirect_uri = "https://YOUR-APP.streamlit.app/oauth2callback"
cookie_secret = "A_LONG_RANDOM_SECRET"
client_id = "YOUR_GOOGLE_CLIENT_ID"
client_secret = "YOUR_GOOGLE_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

Paste production secrets into Streamlit Community Cloud → App settings → Secrets.

## Development market-data adapter

V7 uses Yahoo Finance through yfinance plus FRED for selected macro series. This is for development/research prototyping. Before charging members or redistributing live data commercially, replace the adapter with a provider whose licence permits your intended use.

## Automated markets

- Any FX pair Yahoo can provide directly or synthesize through USD legs
- XAU/XAG crosses
- NQ / MNQ / NQ1!
- ES / MES / ES1!
- BTCUSD
- WTI

## Automated outputs

- Monthly, Weekly, Daily, H4, H1, M30, M15, M5, M1
- Deterministic price classification
- Asset-family-specific automatic drivers
- Trader-style weighting
- Session-tape context
- Buy / Sell / Wait conclusion
- Optional member override
