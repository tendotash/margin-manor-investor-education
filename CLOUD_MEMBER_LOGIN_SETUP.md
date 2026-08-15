# Margin Manor V7.1 — Cloud Member Login Setup

This version is designed so visitors can log in directly from the public Investor Education website.
You do not need to run or test it locally.

## User flow

1. Visitor opens the public Margin Manor Investor Education website.
2. The left sidebar shows **MEMBER ACCESS**.
3. Visitor clicks **Member Login**.
4. Google handles authentication.
5. Streamlit returns the visitor to Margin Manor.
6. If the signed-in email is in `member_emails`, Margin Manor automatically opens
   **Member Live Insight Engine**.
7. The member can later click **Open Live Insights** from the sidebar at any time.
8. Non-members remain able to use the public/free website.

## Step 1 — Upload V7.1 to GitHub

Upload/replace:

- `app.py`
- `premium_engine.py`
- `requirements.txt`
- `assets/style.css`
- `.streamlit/config.toml`
- `.gitignore`

Do not upload a real `.streamlit/secrets.toml`.

## Step 2 — Create Google login

In Google Cloud / Google Auth Platform:

1. Create or select a Google Cloud project.
2. Open **Google Auth Platform**.
3. Configure **Branding**.
4. Under **Audience**, add your own Google account as a test user while the app is in Testing.
5. Open **Clients** → **Create Client**.
6. Choose **Web application**.
7. Add this Authorized Redirect URI:

   `https://YOUR-STREAMLIT-APP.streamlit.app/oauth2callback`

   Replace `YOUR-STREAMLIT-APP` with your actual public Streamlit subdomain.

8. Create the client.
9. Copy the **Client ID** and **Client secret**.

## Step 3 — Add Streamlit Cloud Secrets

Open:

**Streamlit Community Cloud → your app → App settings → Secrets**

Paste:

```toml
member_emails = [
    "YOUR_GOOGLE_EMAIL@gmail.com"
]

[auth]
redirect_uri = "https://YOUR-STREAMLIT-APP.streamlit.app/oauth2callback"
cookie_secret = "REPLACE_WITH_A_LONG_RANDOM_SECRET"
client_id = "REPLACE_WITH_GOOGLE_CLIENT_ID"
client_secret = "REPLACE_WITH_GOOGLE_CLIENT_SECRET"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

For another paid member, add their approved Google email:

```toml
member_emails = [
    "you@gmail.com",
    "member1@gmail.com",
    "member2@gmail.com"
]
```

This is the membership authorization list.

## Step 4 — Make Google accept the same redirect URI

The URI in Google Cloud and the URI in Streamlit Secrets must match exactly:

`https://YOUR-STREAMLIT-APP.streamlit.app/oauth2callback`

## Step 5 — Use the website

Refresh the deployed Margin Manor site.

The sidebar will show **MEMBER ACCESS → Member Login**.

After an approved Google account logs in, the site automatically opens the Member Live Insight Engine.

## Important security note

Google OIDC proves who the person is. Margin Manor then separately checks the email against
`member_emails` before allowing member access.

Never commit the Google client secret or cookie secret to GitHub.
