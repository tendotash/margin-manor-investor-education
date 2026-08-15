# Margin Manor V7.2 — Supabase Member Login

V7.2 removes Google Cloud/OIDC completely.

## Member flow

Public Margin Manor website → Member Access → Email + Password → Supabase Auth
→ public.memberships → Active membership? → Member Live Insight Engine

There is no public registration button. You issue member accounts yourself.

## 1. Supabase
Open your Supabase project and copy the Project URL plus Publishable key
(or legacy anon key). Do not use the service-role/secret key in the public app.

## 2. Create the membership table
Supabase Dashboard → SQL Editor → run `SUPABASE_MEMBERSHIP_SETUP.sql`.

## 3. Create your own login
Supabase Dashboard → Authentication → Users → create your email/password user.
If email confirmation is enabled, confirm the account first. Copy the user UUID.

## 4. Activate your membership
Supabase Dashboard → Table Editor → memberships → add a row:
- user_id: Auth user UUID
- email: login email
- display_name: your name
- plan: Premium
- status: active
- expires_at: blank for no expiry

## 5. Upload V7.2
Upload/replace:
- app.py
- premium_engine.py
- requirements.txt
- assets/style.css
- .streamlit/config.toml

Do not upload a real `.streamlit/secrets.toml`.

## 6. Streamlit Cloud Secrets
App settings → Secrets:

```toml
SUPABASE_URL = "https://YOUR-PROJECT.supabase.co"
SUPABASE_PUBLISHABLE_KEY = "YOUR-PUBLISHABLE-KEY"
```

V7.2 also accepts `SUPABASE_ANON_KEY` for older projects.

## 7. Use it
Reboot/redeploy the app. The public sidebar will show the member email/password form.
An authenticated user only receives Live Insight access when their own membership row
has status `active` and has not expired.

## Adding members later
Create the Supabase Auth user, add their UUID to `memberships`, and set status active.
To revoke access, change status to inactive. To time-limit access, set expires_at.

## Password reset
V7.2 can request a Supabase reset email. A later version can add a dedicated in-app
recovery callback screen to complete the new-password step after opening the email.
