import re
from datetime import datetime, timezone
from io import StringIO
from zoneinfo import ZoneInfo
from urllib.parse import quote

import numpy as np
import pandas as pd
import requests
import streamlit as st
import yfinance as yf
from supabase import create_client


TIMEFRAMES = ["Monthly", "Weekly", "Daily", "H4", "H1", "M30", "M15", "M5", "M1"]
DIR = {"Bullish": 1.0, "Neutral": 0.0, "Bearish": -1.0}

STYLE_TF_WEIGHTS = {
    "Scalper": {"Monthly": 0.00, "Weekly": 0.00, "Daily": 0.03, "H4": 0.05, "H1": 0.10, "M30": 0.12, "M15": 0.20, "M5": 0.28, "M1": 0.22},
    "Day Trader": {"Monthly": 0.03, "Weekly": 0.05, "Daily": 0.12, "H4": 0.18, "H1": 0.22, "M30": 0.17, "M15": 0.12, "M5": 0.08, "M1": 0.03},
    "Session Trader": {"Monthly": 0.02, "Weekly": 0.04, "Daily": 0.10, "H4": 0.16, "H1": 0.22, "M30": 0.20, "M15": 0.14, "M5": 0.08, "M1": 0.04},
    "Swing Trader": {"Monthly": 0.10, "Weekly": 0.22, "Daily": 0.30, "H4": 0.20, "H1": 0.10, "M30": 0.05, "M15": 0.02, "M5": 0.01, "M1": 0.00},
}
STYLE_PRICE_DRIVER_WEIGHTS = {
    "Scalper": (0.80, 0.20),
    "Day Trader": (0.68, 0.32),
    "Session Trader": (0.62, 0.38),
    "Swing Trader": (0.58, 0.42),
}
STYLE_EXEC_TFS = {
    "Scalper": ["M15", "M5", "M1"],
    "Day Trader": ["H4", "H1", "M30", "M15", "M5"],
    "Session Trader": ["H1", "M30", "M15", "M5", "M1"],
    "Swing Trader": ["Weekly", "Daily", "H4", "H1"],
}

CURRENCY_META = {
    "USD": {"risk": 0.10}, "EUR": {"risk": 0.10}, "GBP": {"risk": 0.25},
    "JPY": {"risk": -0.90}, "CHF": {"risk": -0.75}, "CAD": {"risk": 0.55},
    "AUD": {"risk": 0.75}, "NZD": {"risk": 0.70}, "NOK": {"risk": 0.55},
    "SEK": {"risk": 0.40}, "SGD": {"risk": 0.20}, "CNH": {"risk": 0.35},
    "CNY": {"risk": 0.35}, "HKD": {"risk": 0.05}, "MXN": {"risk": 0.80},
    "ZAR": {"risk": 0.90}, "TRY": {"risk": 1.00}, "PLN": {"risk": 0.45},
    "CZK": {"risk": 0.40}, "HUF": {"risk": 0.65}, "DKK": {"risk": 0.05},
    "INR": {"risk": 0.45}, "BRL": {"risk": 0.80}, "KRW": {"risk": 0.65},
    "TWD": {"risk": 0.50}, "IDR": {"risk": 0.55}, "MYR": {"risk": 0.50},
    "THB": {"risk": 0.40}, "PHP": {"risk": 0.45}, "AED": {"risk": 0.05},
    "SAR": {"risk": 0.05},
}

COMMODITY_LINKS = {
    "CAD": ("CL=F", "Oil"), "NOK": ("CL=F", "Oil"), "MXN": ("CL=F", "Oil"),
    "MYR": ("CL=F", "Oil"), "AUD": ("HG=F", "Copper / China-sensitive commodities"),
    "ZAR": ("HG=F", "Industrial metals"), "BRL": ("HG=F", "Industrial commodities"),
    "NZD": ("GC=F", "Broad commodity proxy"),
}

QUICK_PAIRS = [
    "XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD",
    "EURGBP", "EURJPY", "EURCHF", "EURCAD", "EURAUD", "EURNZD", "GBPJPY", "GBPCHF", "GBPCAD",
    "GBPAUD", "GBPNZD", "AUDJPY", "AUDCHF", "AUDCAD", "AUDNZD", "NZDJPY", "NZDCHF", "NZDCAD",
    "CADJPY", "CADCHF", "CHFJPY", "XAUEUR", "XAUGBP", "XAUJPY",
]


def _html(markup):
    st.html(markup)


def _secret(name, default=None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return default



def _secret_bool(name, default=False):
    v = _secret(name, default)
    if isinstance(v, bool):
        return v
    return str(v).lower().strip() in {"1", "true", "yes", "on"}


def _supabase_credentials():
    url = str(_secret("SUPABASE_URL", "") or "").strip()
    key = str(
        _secret("SUPABASE_PUBLISHABLE_KEY", "")
        or _secret("SUPABASE_ANON_KEY", "")
        or _secret("SUPABASE_KEY", "")
        or ""
    ).strip()
    return url, key


def _supabase_configured():
    url, key = _supabase_credentials()
    return bool(url and key)


def _new_supabase_client():
    url, key = _supabase_credentials()
    if not url or not key:
        raise RuntimeError(
            "Supabase is not configured. Add SUPABASE_URL and "
            "SUPABASE_PUBLISHABLE_KEY (or SUPABASE_ANON_KEY) to Streamlit Cloud Secrets."
        )
    return create_client(url, key)


def _clear_auth_session():
    for key in [
        "mm_sb_access_token",
        "mm_sb_refresh_token",
        "mm_sb_user_id",
        "mm_sb_email",
        "mm_sb_name",
        "mm_membership",
        "_mm_member_auto_entry_done",
    ]:
        st.session_state.pop(key, None)


def _save_supabase_session(auth_response):
    session = getattr(auth_response, "session", None)
    user = getattr(auth_response, "user", None)

    if not session or not user:
        raise RuntimeError(
            "No active session was returned. If email confirmation is enabled, "
            "confirm the account before signing in."
        )

    st.session_state["mm_sb_access_token"] = session.access_token
    st.session_state["mm_sb_refresh_token"] = session.refresh_token
    st.session_state["mm_sb_user_id"] = str(user.id)
    st.session_state["mm_sb_email"] = str(user.email or "").strip().lower()

    metadata = getattr(user, "user_metadata", None) or {}
    display_name = (
        metadata.get("display_name")
        or metadata.get("full_name")
        or metadata.get("name")
        or str(user.email or "Member").split("@")[0]
    )
    st.session_state["mm_sb_name"] = str(display_name)


def _restore_supabase_session():
    access_token = st.session_state.get("mm_sb_access_token")
    refresh_token = st.session_state.get("mm_sb_refresh_token")

    if not access_token or not refresh_token or not _supabase_configured():
        return None, None

    try:
        sb = _new_supabase_client()
        session_response = sb.auth.set_session(access_token, refresh_token)
        session = getattr(session_response, "session", None)

        if session:
            st.session_state["mm_sb_access_token"] = session.access_token
            st.session_state["mm_sb_refresh_token"] = session.refresh_token
            access_token = session.access_token

        user_response = sb.auth.get_user(access_token)
        user = getattr(user_response, "user", None)

        if not user:
            _clear_auth_session()
            return None, None

        st.session_state["mm_sb_user_id"] = str(user.id)
        st.session_state["mm_sb_email"] = str(user.email or "").strip().lower()

        metadata = getattr(user, "user_metadata", None) or {}
        st.session_state["mm_sb_name"] = str(
            metadata.get("display_name")
            or metadata.get("full_name")
            or metadata.get("name")
            or str(user.email or "Member").split("@")[0]
        )
        return sb, user
    except Exception:
        _clear_auth_session()
        return None, None


def supabase_login(email, password):
    if not _supabase_configured():
        return False, (
            "Supabase is not connected yet. Add SUPABASE_URL and "
            "SUPABASE_PUBLISHABLE_KEY to Streamlit Cloud Secrets."
        )

    email = str(email or "").strip().lower()
    password = str(password or "")

    if not email or not password:
        return False, "Enter both your email and password."

    try:
        sb = _new_supabase_client()
        response = sb.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        _save_supabase_session(response)
        return True, "Signed in successfully."
    except Exception as exc:
        message = str(exc)
        if "Invalid login credentials" in message:
            return False, "Incorrect email or password."
        if "Email not confirmed" in message:
            return False, "Confirm your email address before signing in."
        return False, f"Login failed: {message}"


def supabase_logout():
    access_token = st.session_state.get("mm_sb_access_token")
    refresh_token = st.session_state.get("mm_sb_refresh_token")

    try:
        if access_token and refresh_token and _supabase_configured():
            sb = _new_supabase_client()
            try:
                sb.auth.set_session(access_token, refresh_token)
            except Exception:
                pass
            try:
                sb.auth.sign_out()
            except Exception:
                pass
    finally:
        _clear_auth_session()


def send_password_reset(email):
    if not _supabase_configured():
        return False, "Supabase is not connected yet."

    email = str(email or "").strip().lower()
    if not email:
        return False, "Enter your email address first."

    try:
        sb = _new_supabase_client()
        redirect_to = str(_secret("PASSWORD_RESET_REDIRECT_URL", "") or "").strip()
        if redirect_to:
            sb.auth.reset_password_for_email(email, {"redirect_to": redirect_to})
        else:
            sb.auth.reset_password_for_email(email)
        return True, "If the account exists, Supabase has sent the password-reset email."
    except Exception as exc:
        return False, f"Could not send the reset email: {exc}"


def _membership_from_supabase(sb, user):
    try:
        response = (
            sb.table("memberships")
            .select("user_id,email,display_name,plan,status,expires_at")
            .eq("user_id", str(user.id))
            .limit(1)
            .execute()
        )
        rows = getattr(response, "data", None) or []
    except Exception as exc:
        return {
            "exists": False,
            "active": False,
            "setup_error": True,
            "message": (
                "Could not read the memberships table. Run the V7.2 Supabase setup SQL "
                "and confirm its RLS policy. "
                f"Technical detail: {exc}"
            ),
        }

    if not rows:
        return {
            "exists": False,
            "active": False,
            "setup_error": False,
            "message": "This account is signed in but does not have a Margin Manor membership record.",
        }

    membership = dict(rows[0])
    status = str(membership.get("status") or "").strip().lower()
    expires_at = membership.get("expires_at")

    not_expired = True
    if expires_at:
        try:
            expiry = pd.to_datetime(expires_at, utc=True)
            now = pd.Timestamp.now(tz="UTC")
            not_expired = bool(expiry > now)
        except Exception:
            not_expired = False

    membership["active"] = status == "active" and not_expired
    membership["exists"] = True
    membership["setup_error"] = False

    if status != "active":
        membership["message"] = f"Membership status: {status or 'inactive'}."
    elif not not_expired:
        membership["message"] = "This membership has expired."
    else:
        membership["message"] = "Active member."
    return membership


def access_state():
    if not _supabase_configured():
        return {
            "allowed": False,
            "mode": "setup_required",
            "email": "",
            "name": "",
            "plan": "",
            "message": "Supabase member login is not configured yet.",
        }

    sb, user = _restore_supabase_session()
    if not sb or not user:
        return {
            "allowed": False,
            "mode": "login",
            "email": "",
            "name": "",
            "plan": "",
            "message": "",
        }

    membership = _membership_from_supabase(sb, user)
    email = str(user.email or "").strip().lower()
    name = (
        membership.get("display_name")
        or st.session_state.get("mm_sb_name")
        or email.split("@")[0]
        or "Member"
    )
    plan = str(membership.get("plan") or "Member")
    st.session_state["mm_membership"] = membership

    if membership.get("active"):
        return {
            "allowed": True,
            "mode": "member",
            "email": email,
            "name": str(name),
            "plan": plan,
            "membership": membership,
            "message": "Active member.",
        }

    return {
        "allowed": False,
        "mode": "denied",
        "email": email,
        "name": str(name),
        "plan": plan,
        "membership": membership,
        "message": membership.get("message", "Membership required."),
    }


def render_access_gate():
    access = access_state()
    if access["allowed"]:
        return access

    _html('''
    <div class="member-lock">
      <div class="member-lock-icon">M</div>
      <div>
        <span>MEMBER ACCESS</span>
        <h2>Margin Manor Live Insight Engine</h2>
        <p>Sign in with your Margin Manor member account to open the automatic Live Insight Engine.</p>
      </div>
    </div>
    ''')

    if access["mode"] == "setup_required":
        st.error(
            "Supabase member login is not configured yet. "
            "Add the two Supabase values to Streamlit Cloud Secrets and run the included setup SQL."
        )
        return None

    if access["mode"] == "login":
        with st.form("member_page_login_form"):
            email = st.text_input("Member Email", key="member_page_email")
            password = st.text_input("Password", type="password", key="member_page_password")
            submitted = st.form_submit_button("Log In", type="primary", use_container_width=True)

        if submitted:
            ok, message = supabase_login(email, password)
            if ok:
                st.session_state["_mm_active_page"] = "Member Live Insight Engine"
                st.session_state["_mm_force_member_page"] = True
                st.rerun()
            else:
                st.error(message)

        with st.expander("Forgot password?"):
            reset_email = st.text_input("Account email", key="member_page_reset_email")
            if st.button("Send Password Reset Email", key="member_page_reset_btn"):
                ok, message = send_password_reset(reset_email)
                (st.success if ok else st.error)(message)
        return None

    st.error(access.get("message") or "Membership required.")
    if st.button("Sign Out", key="member_page_logout_btn"):
        supabase_logout()
        st.session_state["_mm_active_page"] = "Home"
        st.rerun()
    return None


def normalize_symbol(raw):
    s = (raw or "").upper().strip()
    s = re.sub(r"[^A-Z0-9]", "", s)
    aliases = {"GOLD": "XAUUSD", "SILVER": "XAGUSD", "XAU": "XAUUSD", "XAG": "XAGUSD"}
    return aliases.get(s, s)


def resolve_asset(raw):
    s = normalize_symbol(raw)
    if s in {"NQ", "NQ1", "MNQ", "MNQ1", "NAS100", "NASDAQ", "USTEC", "NDX"}:
        return "NQ", "index"
    if s in {"ES", "ES1", "MES", "MES1", "SPX500", "SP500", "US500", "SPX"}:
        return "ES", "index"
    if s in {"BTC", "BTCUSD"}:
        return "BTCUSD", "crypto"
    if s in {"WTI", "USOIL", "CL"}:
        return "WTI", "commodity"
    if len(s) == 6 and s.isalpha():
        if s[:3] in {"XAU", "XAG"}:
            return s, "metal"
        return s, "forex"
    return s, "unknown"


def _norm_df(df):
    if df is None or df.empty:
        return pd.DataFrame()
    d = df.copy()
    if isinstance(d.columns, pd.MultiIndex):
        lvl0 = [str(x) for x in d.columns.get_level_values(0)]
        if any(x in {"Open", "High", "Low", "Close", "Volume"} for x in lvl0):
            d.columns = d.columns.get_level_values(0)
        else:
            d.columns = d.columns.get_level_values(-1)
    d.columns = [str(c).title() for c in d.columns]
    if "Close" not in d.columns:
        return pd.DataFrame()
    for c in ["Open", "High", "Low"]:
        if c not in d.columns:
            d[c] = d["Close"]
    cols = ["Open", "High", "Low", "Close"] + (["Volume"] if "Volume" in d.columns else [])
    d = d[cols].dropna(subset=["Close"])
    return d[~d.index.duplicated(keep="last")].sort_index()


@st.cache_data(ttl=120, show_spinner=False)
def yahoo_chart_download(symbol, interval, period):
    """
    Lightweight fallback that reads Yahoo's chart response directly.
    This avoids some yfinance cookie/crumb failures that can occur on
    hosted Streamlit instances. It remains a development/personal-use feed.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0 Safari/537.36"
        ),
        "Accept": "application/json,text/plain,*/*",
    }
    params = {
        "interval": interval,
        "range": period,
        "includePrePost": "false",
        "events": "div,splits",
    }

    encoded = quote(symbol, safe="")
    hosts = [
        "https://query1.finance.yahoo.com",
        "https://query2.finance.yahoo.com",
    ]

    for host in hosts:
        try:
            url = f"{host}/v8/finance/chart/{encoded}"
            r = requests.get(url, params=params, headers=headers, timeout=15)
            if r.status_code != 200:
                continue

            payload = r.json()
            chart = payload.get("chart", {})
            if chart.get("error"):
                continue

            results = chart.get("result") or []
            if not results:
                continue

            result = results[0]
            timestamps = result.get("timestamp") or []
            indicators = result.get("indicators") or {}
            quotes = indicators.get("quote") or []

            if not timestamps or not quotes:
                continue

            q = quotes[0]
            n = len(timestamps)

            def _series(name):
                values = q.get(name) or [None] * n
                if len(values) < n:
                    values = list(values) + [None] * (n - len(values))
                return values[:n]

            idx = pd.to_datetime(timestamps, unit="s", utc=True)
            d = pd.DataFrame(
                {
                    "Open": _series("open"),
                    "High": _series("high"),
                    "Low": _series("low"),
                    "Close": _series("close"),
                    "Volume": _series("volume"),
                },
                index=idx,
            )
            d = _norm_df(d)
            if not d.empty:
                return d
        except Exception:
            continue

    return pd.DataFrame()


@st.cache_data(ttl=120, show_spinner=False)
def yf_download(symbol, interval, period):
    """
    Development market-data adapter.

    1) Direct Yahoo chart endpoint first.
    2) yfinance fallback second.

    The two routes fail for different reasons, so using both makes the
    Streamlit-hosted development build materially more resilient.
    """
    direct = yahoo_chart_download(symbol, interval, period)
    if not direct.empty:
        return direct

    try:
        try:
            yf.config.network.retries = 2
        except Exception:
            pass

        try:
            d = yf.download(
                symbol,
                interval=interval,
                period=period,
                auto_adjust=False,
                progress=False,
                threads=False,
                repair=True,
                timeout=15,
            )
        except TypeError:
            d = yf.download(
                symbol,
                interval=interval,
                period=period,
                auto_adjust=False,
                progress=False,
                threads=False,
                repair=True,
            )
        except Exception:
            d = yf.download(
                symbol,
                interval=interval,
                period=period,
                auto_adjust=False,
                progress=False,
                threads=False,
            )

        return _norm_df(d)
    except Exception:
        return pd.DataFrame()


def invert_ohlc(d):
    if d.empty:
        return d
    out = pd.DataFrame(index=d.index)
    out["Open"] = 1 / d["Open"].replace(0, np.nan)
    out["High"] = 1 / d["Low"].replace(0, np.nan)
    out["Low"] = 1 / d["High"].replace(0, np.nan)
    out["Close"] = 1 / d["Close"].replace(0, np.nan)
    return out.dropna(subset=["Close"])


def ratio_ohlc(a, b):
    if a.empty or b.empty:
        return pd.DataFrame()
    idx = a.index.intersection(b.index)
    if len(idx) < 10:
        return pd.DataFrame()
    x, y = a.loc[idx], b.loc[idx]
    out = pd.DataFrame(index=idx)
    out["Open"] = x["Open"] / y["Open"].replace(0, np.nan)
    out["High"] = x["High"] / y["Low"].replace(0, np.nan)
    out["Low"] = x["Low"] / y["High"].replace(0, np.nan)
    out["Close"] = x["Close"] / y["Close"].replace(0, np.nan)
    return out.dropna(subset=["Close"])


def currency_usd_ohlc(cur, interval, period):
    cur = cur.upper()
    if cur == "USD":
        return pd.DataFrame()
    d = yf_download(f"{cur}USD=X", interval, period)
    if not d.empty:
        return d
    inv = yf_download(f"USD{cur}=X", interval, period)
    return invert_ohlc(inv) if not inv.empty else pd.DataFrame()


def fx_ohlc(pair, interval, period):
    direct = yf_download(f"{pair}=X", interval, period)
    if not direct.empty:
        return direct, f"Yahoo Finance {pair}=X"
    base, quote = pair[:3], pair[3:]
    if base == "USD":
        q = currency_usd_ohlc(quote, interval, period)
        return (invert_ohlc(q), f"Synthetic {pair} from USD/{quote}") if not q.empty else (pd.DataFrame(), "Unavailable")
    if quote == "USD":
        b = currency_usd_ohlc(base, interval, period)
        return (b, f"Synthetic {pair} from {base}/USD") if not b.empty else (pd.DataFrame(), "Unavailable")
    b, q = currency_usd_ohlc(base, interval, period), currency_usd_ohlc(quote, interval, period)
    if not b.empty and not q.empty:
        return ratio_ohlc(b, q), f"Synthetic {pair} from USD legs"
    return pd.DataFrame(), "Unavailable"


def metal_ohlc(pair, interval, period):
    metal, quote = pair[:3], pair[3:]
    ticker = "GC=F" if metal == "XAU" else "SI=F"
    base = yf_download(ticker, interval, period)
    if base.empty:
        return pd.DataFrame(), f"{ticker} unavailable"
    if quote == "USD":
        return base, f"Yahoo Finance {ticker} proxy"
    q = currency_usd_ohlc(quote, interval, period)
    if q.empty:
        return pd.DataFrame(), f"{quote} FX leg unavailable"
    return ratio_ohlc(base, q), f"Synthetic {pair} from {ticker} + {quote} FX leg"


def fetch_asset(asset, interval, period):
    symbol, kind = resolve_asset(asset)
    if kind == "forex":
        return fx_ohlc(symbol, interval, period)
    if kind == "metal":
        return metal_ohlc(symbol, interval, period)
    mapping = {"NQ": ("NQ=F", "NQ futures"), "ES": ("ES=F", "ES futures"), "BTCUSD": ("BTC-USD", "Bitcoin"), "WTI": ("CL=F", "WTI futures")}
    if symbol in mapping:
        t, label = mapping[symbol]
        return yf_download(t, interval, period), f"Yahoo Finance {label}"
    return pd.DataFrame(), "Unsupported"


def resample_ohlc(d, rule):
    if d.empty or not rule:
        return d
    agg = {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
    if "Volume" in d.columns:
        agg["Volume"] = "sum"
    try:
        return d.resample(rule).agg(agg).dropna(subset=["Close"])
    except Exception:
        return pd.DataFrame()


def rsi(close, n=14):
    delta = close.diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    gain = up.ewm(alpha=1/n, adjust=False).mean()
    loss = down.ewm(alpha=1/n, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - 100/(1+rs)


def classify_tf(d):
    if d is None or len(d) < 55:
        return {"state": "Neutral", "score": 0.0, "structure": "Insufficient data", "trend": "Insufficient data", "momentum": "Insufficient data", "bars": 0 if d is None else len(d)}
    x = d.dropna(subset=["Close"]).copy()
    close = x["Close"].astype(float)
    e20 = close.ewm(span=20, adjust=False).mean()
    e50 = close.ewm(span=50, adjust=False).mean()
    rr, pp = x.iloc[-8:], x.iloc[-16:-8]
    tol = 0.00025
    hh = rr["High"].max() > pp["High"].max()*(1+tol)
    hl = rr["Low"].min() > pp["Low"].min()*(1+tol)
    lh = rr["High"].max() < pp["High"].max()*(1-tol)
    ll = rr["Low"].min() < pp["Low"].min()*(1-tol)
    if hh and hl:
        ss, stxt = 1.0, "Higher-high / higher-low"
    elif lh and ll:
        ss, stxt = -1.0, "Lower-high / lower-low"
    else:
        ss, stxt = 0.0, "Mixed / range"
    last = float(close.iloc[-1]); a = float(e20.iloc[-1]); b = float(e50.iloc[-1]); prev = float(e20.iloc[-5])
    slope = (a-prev)/max(abs(last), 1e-9)
    if last > a > b and slope > 0:
        ts, ttxt = 1.0, "Price > EMA20 > EMA50; EMA20 rising"
    elif last < a < b and slope < 0:
        ts, ttxt = -1.0, "Price < EMA20 < EMA50; EMA20 falling"
    elif last > a and a >= b:
        ts, ttxt = 0.5, "Positive trend; partial EMA alignment"
    elif last < a and a <= b:
        ts, ttxt = -0.5, "Negative trend; partial EMA alignment"
    else:
        ts, ttxt = 0.0, "EMA structure mixed"
    rv = rsi(close).iloc[-1]
    rv = float(rv) if pd.notna(rv) else 50.0
    ret5 = float(close.iloc[-1]/close.iloc[-6]-1) if close.iloc[-6] else 0.0
    if ret5 > 0 and rv >= 52:
        ms, mtxt = 1.0, f"Positive momentum · RSI {rv:.1f}"
    elif ret5 < 0 and rv <= 48:
        ms, mtxt = -1.0, f"Negative momentum · RSI {rv:.1f}"
    else:
        ms, mtxt = 0.0, f"Mixed momentum · RSI {rv:.1f}"
    score = 0.45*ss + 0.35*ts + 0.20*ms
    state = "Bullish" if score >= 0.22 else "Bearish" if score <= -0.22 else "Neutral"
    return {"state": state, "score": float(score), "structure": stxt, "trend": ttxt, "momentum": mtxt, "bars": len(x), "last": last}


def auto_timeframes(asset):
    daily, ds = fetch_asset(asset, "1d", "5y")
    hourly, hs = fetch_asset(asset, "1h", "60d")
    five, fs = fetch_asset(asset, "5m", "60d")
    one, os = fetch_asset(asset, "1m", "7d")

    # Yahoo can occasionally refuse 1-minute history while still returning
    # the other intraday granularities. A 2-minute proxy is used only as a
    # last-resort development fallback and is explicitly labelled as such.
    m1_proxy = False
    if one.empty or len(one) < 55:
        two, ts = fetch_asset(asset, "2m", "30d")
        if not two.empty and len(two) >= 55:
            one = two
            os = f"{ts} · 2-minute proxy for M1"
            m1_proxy = True

    frames = {
        "Monthly": resample_ohlc(daily, "ME"),
        "Weekly": resample_ohlc(daily, "W-FRI"),
        "Daily": daily,
        "H4": resample_ohlc(hourly, "4h"),
        "H1": hourly,
        "M30": resample_ohlc(five, "30min"),
        "M15": resample_ohlc(five, "15min"),
        "M5": five,
        "M1": one,
    }
    src = {
        "Monthly": ds, "Weekly": ds, "Daily": ds,
        "H4": hs, "H1": hs,
        "M30": fs, "M15": fs, "M5": fs,
        "M1": os,
    }

    out = {}
    for tf in TIMEFRAMES:
        out[tf] = classify_tf(frames[tf])
        out[tf]["source"] = src[tf]
        out[tf]["last_timestamp"] = (
            str(frames[tf].index[-1]) if not frames[tf].empty else "Unavailable"
        )
        out[tf]["available"] = bool(len(frames[tf]) >= 55)
        out[tf]["proxy"] = bool(tf == "M1" and m1_proxy)

    return out


@st.cache_data(ttl=1800, show_spinner=False)
def fred_series(series_id):
    try:
        r = requests.get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}", timeout=12, headers={"User-Agent":"MarginManor/1.0"})
        r.raise_for_status()
        d = pd.read_csv(StringIO(r.text))
        dc, vc = d.columns[0], d.columns[1]
        d[dc] = pd.to_datetime(d[dc], errors="coerce")
        d[vc] = pd.to_numeric(d[vc], errors="coerce")
        return d.dropna().set_index(dc)[vc].sort_index()
    except Exception:
        return pd.Series(dtype=float)


def style_source(style):
    if style == "Scalper": return "5m", "5d", 12
    if style in {"Day Trader", "Session Trader"}: return "1h", "30d", 12
    return "1d", "1y", 20


def direction_from_close(close, lookback=12):
    s = pd.Series(close).dropna().astype(float)
    if len(s) < max(20, lookback+5):
        return 0.0, "Neutral"
    lb = min(lookback, len(s)-2)
    ret = float(s.iloc[-1]/s.iloc[-1-lb]-1) if s.iloc[-1-lb] else 0.0
    fast = s.ewm(span=8, adjust=False).mean(); slow = s.ewm(span=21, adjust=False).mean()
    ed = float((fast.iloc[-1]-slow.iloc[-1])/max(abs(s.iloc[-1]), 1e-9))
    vol = s.pct_change().rolling(20).std().iloc[-1]
    vol = float(vol) if pd.notna(vol) else 0.0
    threshold = max(vol*0.75, 0.00015)
    combined = 0.65*ret + 0.35*ed
    if combined > threshold: return 1.0, "Rising"
    if combined < -threshold: return -1.0, "Falling"
    return 0.0, "Neutral"


def direction_symbol(symbol, style):
    interval, period, lb = style_source(style)
    d = yf_download(symbol, interval, period)
    if d.empty: return 0.0, "Neutral", "Unavailable", f"Yahoo Finance {symbol}"
    sc, state = direction_from_close(d["Close"], lb)
    return sc, state, str(d.index[-1]), f"Yahoo Finance {symbol}"


def direction_fred(series, style):
    s = fred_series(series)
    if s.empty: return 0.0, "Neutral", "Unavailable", f"FRED {series}"
    lb = 5 if style == "Scalper" else 10 if style in {"Day Trader", "Session Trader"} else 20
    sc, state = direction_from_close(s, lb)
    return sc, state, str(s.index[-1].date()), f"FRED {series}"


def ratio_direction(a, b, style, label):
    interval, period, lb = style_source(style)
    x, y = yf_download(a, interval, period), yf_download(b, interval, period)
    if x.empty or y.empty: return 0.0, "Neutral", "Unavailable", label
    idx = x.index.intersection(y.index)
    if len(idx) < 20: return 0.0, "Neutral", "Unavailable", label
    sc, state = direction_from_close(x.loc[idx,"Close"] / y.loc[idx,"Close"].replace(0,np.nan), lb)
    return sc, state, str(idx[-1]), label


def currency_usd_direction(cur, style):
    if cur == "USD":
        return direction_symbol("DX-Y.NYB", style)
    interval, period, lb = style_source(style)
    d = currency_usd_ohlc(cur, interval, period)
    if d.empty: return 0.0, "Neutral", "Unavailable", f"{cur} USD-relative FX"
    sc, state = direction_from_close(d["Close"], lb)
    return sc, state, str(d.index[-1]), f"{cur} USD-relative FX"


def driver_row(name, tier, weight, raw, multiplier, state, source, freshness, note):
    effect = float(np.clip(raw*multiplier, -1, 1))
    weighted = effect*weight
    impact = "Strong Tailwind" if weighted >= 0.9 else "Tailwind" if effect > 0 else "Strong Headwind" if weighted <= -0.9 else "Headwind" if effect < 0 else "Neutral"
    return {"name":name,"tier":tier,"weight":float(weight),"input":state,"effect":effect,"weighted_effect":weighted,"impact":impact,"source":source,"freshness":freshness,"note":note}


def commodity_rows(base, quote, style):
    rows=[]
    for cur, role in [(base,"base"),(quote,"quote")]:
        if cur not in COMMODITY_LINKS: continue
        ticker,label = COMMODITY_LINKS[cur]
        raw,state,ts,src = direction_symbol(ticker, style)
        rows.append(driver_row(f"{cur} Commodity Link — {label}","Context",0.55,raw,0.45 if role=="base" else -0.45,state,src,ts,"Commodity-sensitive currency overlay."))
    return rows


def auto_drivers(asset, style):
    symbol, kind = resolve_asset(asset); rows=[]
    def add(name,tier,weight,fn,mult,note):
        raw,state,ts,src = fn(); rows.append(driver_row(name,tier,weight,raw,mult,state,src,ts,note))

    if kind == "metal":
        metal, quote = symbol[:3], symbol[3:]
        add("DXY / US Dollar","Primary",1.20,lambda:direction_symbol("DX-Y.NYB",style),-1.0,"Broad USD direction.")
        add("US 10Y Yield","Primary",1.05,lambda:direction_symbol("^TNX",style),-1.0,"Treasury-yield pressure.")
        add("US Real Yield","Primary",1.30,lambda:direction_fred("DFII10",style),-1.0,"Real-yield opportunity-cost channel.")
        add("US 2Y / Policy-Rate Proxy","Primary",0.95,lambda:direction_fred("DGS2",style),-0.85,"Transparent policy/rates proxy; not the Fed's actual forecast.")
        add("Silver Confirmation" if metal=="XAU" else "Gold Confirmation","Confirmation",0.65,lambda:direction_symbol("SI=F" if metal=="XAU" else "GC=F",style),0.75,"Cross-metal confirmation.")
        add("VIX / Risk Stress","Context",0.45,lambda:direction_symbol("^VIX",style),0.40,"Safe-haven context, not mechanical.")
        add("Oil / Inflation Context","Context",0.35,lambda:direction_symbol("CL=F",style),0.30,"Secondary inflation context.")
        add("10Y Breakeven Inflation","Macro",0.55,lambda:direction_fred("T10YIE",style),0.55,"Inflation-expectations context.")
        if quote != "USD":
            raw,state,ts,src = currency_usd_direction(quote, style)
            rows.append(driver_row(f"{quote} Currency Strength","Primary",0.95,raw,-1.0,state,src,ts,"Stronger quote currency pressures the metal cross."))
        return rows

    if symbol == "NQ":
        specs=[
            ("US 10Y Yield","Primary",1.10,lambda:direction_symbol("^TNX",style),-1.0,"Rates/valuation pressure."),
            ("US Real Yield","Primary",1.15,lambda:direction_fred("DFII10",style),-1.0,"Real discount-rate pressure."),
            ("US 2Y / Policy-Rate Proxy","Primary",0.95,lambda:direction_fred("DGS2",style),-0.85,"Front-end rates proxy."),
            ("VIX","Primary",1.00,lambda:direction_symbol("^VIX",style),-1.0,"Equity volatility/stress."),
            ("Semiconductors / SOXX","Confirmation",0.85,lambda:direction_symbol("SOXX",style),0.90,"Nasdaq leadership confirmation."),
            ("ES / Broad Equity","Confirmation",0.65,lambda:direction_symbol("ES=F",style),0.70,"Broad equity confirmation."),
            ("DXY","Context",0.35,lambda:direction_symbol("DX-Y.NYB",style),-0.35,"Financial-conditions context."),
            ("High Yield Credit Spread","Primary",0.80,lambda:direction_fred("BAMLH0A0HYM2",style),-0.90,"Credit-stress proxy."),
            ("Breadth Proxy — RSP/SPY","Confirmation",0.75,lambda:ratio_direction("RSP","SPY",style,"RSP/SPY"),0.85,"Equal-weight breadth proxy."),
        ]
        for x in specs: add(*x)
        return rows

    if symbol == "ES":
        specs=[
            ("US 10Y Yield","Primary",1.00,lambda:direction_symbol("^TNX",style),-0.85,"Rates/valuation pressure."),
            ("US 2Y / Policy-Rate Proxy","Primary",0.90,lambda:direction_fred("DGS2",style),-0.80,"Front-end rates proxy."),
            ("VIX","Primary",1.15,lambda:direction_symbol("^VIX",style),-1.0,"Broad-equity volatility."),
            ("High Yield Credit Spread","Primary",1.05,lambda:direction_fred("BAMLH0A0HYM2",style),-1.0,"Credit stress."),
            ("NQ / Growth Leadership","Confirmation",0.70,lambda:direction_symbol("NQ=F",style),0.75,"Growth leadership."),
            ("Breadth Proxy — RSP/SPY","Confirmation",0.85,lambda:ratio_direction("RSP","SPY",style,"RSP/SPY"),0.90,"Equal-weight breadth proxy."),
            ("Financials — XLF/SPY","Confirmation",0.55,lambda:ratio_direction("XLF","SPY",style,"XLF/SPY"),0.60,"Financial participation."),
            ("Cyclicals — XLI/SPY","Confirmation",0.50,lambda:ratio_direction("XLI","SPY",style,"XLI/SPY"),0.55,"Cyclical participation."),
            ("DXY","Context",0.30,lambda:direction_symbol("DX-Y.NYB",style),-0.30,"Financial-conditions context."),
        ]
        for x in specs: add(*x)
        return rows

    if symbol == "BTCUSD":
        specs=[
            ("DXY","Primary",0.90,lambda:direction_symbol("DX-Y.NYB",style),-0.85,"Liquidity headwind/tailwind."),
            ("US Real Yield","Primary",0.90,lambda:direction_fred("DFII10",style),-0.85,"Real-rate conditions."),
            ("NQ / Growth-Risk Proxy","Confirmation",0.80,lambda:direction_symbol("NQ=F",style),0.80,"Risk/liquidity confirmation."),
            ("VIX","Primary",0.80,lambda:direction_symbol("^VIX",style),-0.80,"Risk-stress proxy."),
            ("SPY / Broad Risk","Confirmation",0.55,lambda:direction_symbol("SPY",style),0.60,"Broad risk confirmation."),
        ]
        for x in specs: add(*x)
        return rows

    if symbol == "WTI":
        specs=[
            ("DXY","Primary",0.75,lambda:direction_symbol("DX-Y.NYB",style),-0.70,"Dollar-priced commodity channel."),
            ("ES / Growth-Risk Proxy","Macro",0.60,lambda:direction_symbol("ES=F",style),0.60,"Market-based growth/risk proxy."),
            ("Copper / Growth Proxy","Macro",0.65,lambda:direction_symbol("HG=F",style),0.65,"Industrial-demand proxy."),
            ("VIX","Context",0.45,lambda:direction_symbol("^VIX",style),-0.50,"Risk-stress context."),
            ("10Y Breakeven Inflation","Macro",0.55,lambda:direction_fred("T10YIE",style),0.50,"Inflation context."),
        ]
        for x in specs: add(*x)
        return rows

    if kind == "forex" and len(symbol)==6:
        base, quote = symbol[:3], symbol[3:]
        br,bs,bts,bsrc = currency_usd_direction(base, style)
        qr,qs,qts,qsrc = currency_usd_direction(quote, style)
        rows.append(driver_row(f"{base} USD-Relative Strength","Primary",1.00,br,1.0,bs,bsrc,bts,"Base-currency strength supports the pair."))
        rows.append(driver_row(f"{quote} USD-Relative Strength","Primary",1.00,qr,-1.0,qs,qsrc,qts,"Quote-currency strength pressures the pair."))
        diff = float(np.clip(br-qr,-1,1))
        state = "Base Stronger" if diff>0.15 else "Quote Stronger" if diff<-0.15 else "Balanced"
        rows.append(driver_row(f"{base} vs {quote} Relative Strength","Primary",1.15,diff,1.0,state,"Derived from USD-relative legs",max(bts,qts),"Relative-strength differential."))
        if base=="USD" or quote=="USD":
            mult = 1.0 if base=="USD" else -1.0
            add("DXY / Broad USD","Confirmation",0.75,lambda:direction_symbol("DX-Y.NYB",style),mult,"Broad USD confirmation.")
            add("US 2Y / USD Rates Proxy","Rates",0.80,lambda:direction_fred("DGS2",style),0.75*mult,"USD front-end rate support.")
        beta = CURRENCY_META.get(base,{}).get("risk",0.0)-CURRENCY_META.get(quote,{}).get("risk",0.0)
        if abs(beta)>=0.20:
            add("VIX / Relative Risk Sensitivity","Context",0.55,lambda:direction_symbol("^VIX",style),-float(np.clip(beta,-1,1)),"Rising stress favors the relatively defensive currency.")
            add("ES / Risk-On Confirmation","Context",0.40,lambda:direction_symbol("ES=F",style),float(np.clip(beta,-1,1)),"Broad risk-on confirmation.")
        rows.extend(commodity_rows(base,quote,style))
        return rows

    return rows


def session_tape(asset, session):
    if session=="Not session-specific": return None
    d,src = fetch_asset(asset,"5m","10d")
    if d.empty or len(d)<20: return None
    idx=d.index
    if idx.tz is None:
        try: idx=idx.tz_localize("UTC")
        except Exception: return None
    ny=idx.tz_convert("America/New_York")
    x=d.copy(); x["day"]=ny.date; x["minute"]=ny.hour*60+ny.minute
    windows={"Asia":(20*60,23*60+59),"London":(2*60,5*60+59),"New York AM":(8*60,12*60),"New York PM":(14*60,17*60+30)}
    a,b=windows.get(session,(0,1439)); candidates=[]
    for day,g in x.groupby("day"):
        sg=g[(g["minute"]>=a)&(g["minute"]<=b)]
        if len(sg)>=4: candidates.append((day,sg))
    if not candidates: return None
    day,sg=candidates[-1]; op=float(sg["Open"].iloc[0]); cl=float(sg["Close"].iloc[-1]); change=cl/op-1 if op else 0
    vol_raw = sg["Close"].pct_change().std()
    vol = float(vol_raw) if pd.notna(vol_raw) else 0.0
    th=max(vol*0.8,0.00015)
    direction=1 if change>th else -1 if change<-th else 0; state="Bullish" if direction>0 else "Bearish" if direction<0 else "Neutral"
    return {"state":state,"direction":direction,"change_pct":change*100,"date":str(day),"bars":len(sg),"source":src}


def group_score(tfs,names): return sum(DIR[tfs[n]] for n in names)/len(names)

def state_from_score(x,th=0.45): return "Bullish" if x>=th else "Bearish" if x<=-th else "Mixed / Neutral"

def driver_env(x): return "Strong Tailwind" if x>=0.60 else "Supportive" if x>=0.20 else "Strong Headwind" if x<=-0.60 else "Adverse" if x<=-0.20 else "Mixed / Neutral"


def analyze(asset,style,session,tf_details,drivers):
    tfs={tf:tf_details[tf]["state"] for tf in TIMEFRAMES}
    base_weights=STYLE_TF_WEIGHTS[style]

    available_tfs = [
        tf for tf in TIMEFRAMES
        if tf_details.get(tf, {}).get("available", tf_details.get(tf, {}).get("bars", 0) >= 55)
        and base_weights.get(tf, 0) > 0
    ]
    available_weight = sum(base_weights[tf] for tf in available_tfs)

    if available_weight > 0:
        ps = sum(
            DIR[tfs[tf]] * (base_weights[tf] / available_weight)
            for tf in available_tfs
        )
    else:
        ps = 0.0

    tw=sum(r["weight"] for r in drivers)
    ds=sum(r["weighted_effect"] for r in drivers)/tw if tw else 0

    pw,dw=STYLE_PRICE_DRIVER_WEIGHTS[style]

    # If driver data is unavailable, do not pretend it is neutral evidence:
    # shift the combined model toward the component that actually exists.
    usable_drivers = [r for r in drivers if r.get("freshness") != "Unavailable"]
    if not usable_drivers:
        pw, dw = 1.0, 0.0

    combined=ps*pw+ds*dw
    sm=session_tape(asset,session)
    if sm and style=="Session Trader":
        combined += 0.05*sm["direction"]
    combined=float(np.clip(combined,-1,1))

    bd=1 if combined>=0.20 else -1 if combined<=-0.20 else 0
    bias="LOOK FOR BUYS" if bd>0 else "LOOK FOR SELLS" if bd<0 else "WAIT / NO CLEAR EDGE"

    lt=group_score(tfs,["Monthly","Weekly"])
    ht=group_score(tfs,["Daily","H4"])
    intr=group_score(tfs,["H1","M30"])
    ex=(0.4*DIR[tfs["M15"]]+0.4*DIR[tfs["M5"]]+0.2*DIR[tfs["M1"]])

    if bd==0:
        ready=0
        rlabel="WAIT — BIAS NOT CLEAR"
    else:
        rel=[
            t for t in STYLE_EXEC_TFS[style]
            if tf_details.get(t, {}).get("available", tf_details.get(t, {}).get("bars", 0) >= 55)
        ]
        if rel:
            aligned=sum(
                1 if DIR[tfs[t]]==bd else 0.35 if DIR[tfs[t]]==0 else 0
                for t in rel
            )
            ready=round(100*aligned/len(rel))
        else:
            ready=0

        if sm and style in {"Day Trader","Session Trader"}:
            ready=min(100,ready+8) if sm["direction"]==bd else max(0,ready-12) if sm["direction"]==-bd else ready

        conflict=ps*ds<-0.18
        rlabel=(
            "FAVOR SETUPS — ALIGNMENT PRESENT"
            if ready>=70 and not conflict
            else "WAIT FOR CONFIRMATION"
            if ready>=45
            else "LOW READINESS — STRUCTURAL CONFLICT"
        )

    total_weight = sum(base_weights.values())
    data_weight = sum(base_weights[tf] for tf in available_tfs)
    price_coverage = round(100 * data_weight / total_weight) if total_weight else 0

    return {
        "asset":asset,"style":style,"session":session,
        "tfs":tfs,"drivers":drivers,
        "price_score":ps,"driver_score":ds,"combined":combined,
        "price_strength":round(ps*100),"driver_strength":round(ds*100),
        "strength":round(abs(combined)*100),
        "bias":bias,"bias_dir":bd,
        "readiness":rlabel,"readiness_score":ready,
        "lt":state_from_score(lt),"ht":state_from_score(ht),
        "intraday":state_from_score(intr),"execution":state_from_score(ex,0.25),
        "driver_environment":driver_env(ds),
        "session_meta":sm,
        "available_tfs":available_tfs,
        "price_coverage":price_coverage,
        "driver_coverage":round(
            100 * len(usable_drivers) / len(drivers)
        ) if drivers else 0,
    }


def apply_overrides(tf_details,drivers):
    if not st.session_state.get("premium_override_enabled",False): return tf_details,drivers
    t={k:dict(v) for k,v in tf_details.items()}; d=[dict(x) for x in drivers]
    st.markdown('<div class="section-title">MANUAL OVERRIDE</div>',unsafe_allow_html=True)
    st.caption("Auto remains the default. Overrides change the final calculation but the audit table still identifies automatic sources.")
    a,b=st.tabs(["Timeframes","Drivers"])
    with a:
        cols=st.columns(3)
        for i,tf in enumerate(TIMEFRAMES):
            with cols[i%3]:
                v=st.selectbox(tf,["Auto","Bullish","Neutral","Bearish"],key=f"premium_otf_{tf}")
                if v!="Auto": t[tf]["state"]=v; t[tf]["override"]=True
    with b:
        cols=st.columns(2)
        for i,row in enumerate(d):
            with cols[i%2]:
                v=st.selectbox(row["name"],["Auto","Tailwind","Neutral","Headwind"],key=f"premium_od_{i}_{re.sub('[^A-Za-z0-9]','_',row['name'])}")
                if v!="Auto":
                    e=1.0 if v=="Tailwind" else -1.0 if v=="Headwind" else 0.0
                    row["input"]=f"Manual {v}"; row["effect"]=e; row["weighted_effect"]=e*row["weight"]; row["impact"]=v; row["override"]=True
    return t,d


def structure_narrative(r):
    parts=[]
    if r["lt"]=="Bullish" and r["ht"]=="Bearish": parts.append("Monthly/Weekly remain bullish while Daily/H4 are bearish, consistent with a higher-timeframe correction inside a broader bullish structure.")
    elif r["lt"]=="Bearish" and r["ht"]=="Bullish": parts.append("Monthly/Weekly remain bearish while Daily/H4 are bullish, consistent with a counter-trend rally or reversal attempt.")
    elif r["lt"]==r["ht"] and r["lt"]!="Mixed / Neutral": parts.append(f"Long-term and higher-timeframe structure are aligned {r['lt'].lower()}.")
    else: parts.append("The higher timeframes are not fully synchronized, so structure is mixed rather than cleanly trending.")
    parts.append(f"Intraday structure is {r['intraday'].lower()} and execution structure is {r['execution'].lower()}.")
    return " ".join(parts)


def driver_narrative(r):
    pos=sorted([x for x in r["drivers"] if x["weighted_effect"]>0],key=lambda x:abs(x["weighted_effect"]),reverse=True)
    neg=sorted([x for x in r["drivers"] if x["weighted_effect"]<0],key=lambda x:abs(x["weighted_effect"]),reverse=True)
    s=f"The automatic driver environment is {r['driver_environment'].lower()}."
    if pos: s += " Strongest tailwinds: " + ", ".join(f"{x['name']} ({x['input']})" for x in pos[:3]) + "."
    if neg: s += " Main headwinds: " + ", ".join(f"{x['name']} ({x['input']})" for x in neg[:3]) + "."
    return s


def conclusion_reason(r):
    if r["bias_dir"]==0: return "Price structure and automatic drivers do not separate enough to justify a directional preference. Waiting is preferable to forcing a trade."
    side="buy" if r["bias_dir"]>0 else "sell"; ps=r["price_score"]*r["bias_dir"]>0.10; ds=r["driver_score"]*r["bias_dir"]>0.10
    if ps and ds: return f"The {side}-side preference is supported by both style-weighted price structure and the automatic driver environment."
    if ps: return f"The {side}-side preference is led by price structure, but drivers are not fully confirming it; execution confirmation matters more."
    if ds: return f"The {side}-side preference is led by the driver environment while price remains conflicted; treat the thesis as conditional."
    return "The combined score is only marginally directional and contains meaningful conflict."


def confirm_lists(r):
    if r["bias_dir"]==0: return ["Wait for the relevant trading-style timeframes to develop clearer alignment.","Wait for the driver environment to move away from neutral."],["Avoid manufacturing a trade while price and drivers remain balanced."]
    desired="Bullish" if r["bias_dir"]>0 else "Bearish"; opposite="Bearish" if desired=="Bullish" else "Bullish"; c=[]; w=[]
    for tf in STYLE_EXEC_TFS[r["style"]]:
        if r["tfs"][tf]!=desired: c.append(f"{tf} turns {desired.lower()} to align with the preferred direction.")
        elif len(w)<3: w.append(f"{tf} flips {opposite.lower()}, weakening the current {desired.lower()} alignment.")
    sup=sorted([x for x in r["drivers"] if x["weighted_effect"]*r["bias_dir"]>0],key=lambda x:abs(x["weighted_effect"]),reverse=True)
    opp=sorted([x for x in r["drivers"] if x["weighted_effect"]*r["bias_dir"]<0],key=lambda x:abs(x["weighted_effect"]),reverse=True)
    for x in sup[:2]: c.append(f"{x['name']} remains {x['input'].lower()}, preserving a {x['impact'].lower()}.")
    for x in opp[:2]: w.append(f"{x['name']} remains {x['input'].lower()}, currently a {x['impact'].lower()}.")
    return list(dict.fromkeys(c))[:5],list(dict.fromkeys(w))[:5]


def member_live_insight_page():
    access=render_access_gate()
    if not access: return

    _html(f'''<div class="member-hero"><div><div class="member-kicker">EXCLUSIVE MEMBER TOOL</div><h1>Margin Manor Live Insight Engine</h1><p>Select the market and trading horizon. Margin Manor automatically classifies all nine timeframes, evaluates observable market and macro drivers, and produces a structured buy-side, sell-side or wait thesis.</p></div><div class="member-status-card"><span>ACCESS</span><strong>{'OWNER PREVIEW' if access['mode']=='preview' else 'ACTIVE MEMBER'}</strong><small>{access['email']}</small></div></div>''')
    st.info("Development data adapter: direct Yahoo chart data with yfinance fallback, plus FRED for selected macro series. The engine now exposes data coverage and degraded-mode handling. Replace the development feed with a licensed commercial provider before selling or redistributing live data to members.")

    st.markdown('<div class="section-title">1. LIVE ANALYSIS PROFILE</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns([1.35,1,1],gap="medium")
    with c1:
        mode=st.selectbox("Market",["Enter Any Pair / Symbol","Quick FX / Metals","Index Futures / Other"],key="premium_asset_mode")
        if mode=="Enter Any Pair / Symbol": raw=st.text_input("Pair / Symbol",value="XAUUSD",key="premium_custom_asset",placeholder="XAUUSD, EURUSD, GBPJPY, NQ, ES, MNQ, MES...")
        elif mode=="Quick FX / Metals": raw=st.selectbox("Pair",QUICK_PAIRS,key="premium_quick_asset")
        else: raw=st.selectbox("Market",["NQ","MNQ","ES","MES","BTCUSD","WTI"],key="premium_other_asset")
        asset,kind=resolve_asset(raw)
    with c2: style=st.selectbox("Trading Style",["Scalper","Day Trader","Session Trader","Swing Trader"],index=1,key="premium_style")
    with c3:
        session=st.selectbox("Trading Session" if style=="Session Trader" else "Session Context",["Asia","London","New York AM","New York PM"] if style=="Session Trader" else ["Not session-specific","Asia","London","New York AM","New York PM"],key="premium_session")

    desc = f"{asset[:3]} is the base and {asset[3:]} is the quote." if kind in {"forex","metal"} and len(asset)==6 else "Dedicated automatic driver model for this market family."
    _html(f'<div class="premium-pair-card"><span>ANALYSIS TARGET</span><strong>{asset}</strong><p>{desc}</p></div>')
    a,b,c=st.columns([1,1.2,2.8])
    with a:
        if st.button("Run Live Analysis",type="primary",use_container_width=True): st.session_state["premium_active"]=True
    with b: st.toggle("Manual Override",key="premium_override_enabled",help="Auto remains the default.")
    with c: st.caption("The engine reads recent market data on demand. Cached requests reduce repeated provider calls.")
    if not st.session_state.get("premium_active",False):
        _html('<div class="premium-ready"><strong>Automatic analysis is ready.</strong><span>Select your market, style and session context, then click Run Live Analysis.</span></div>'); return

    with st.spinner(f"Reading {asset} across 9 timeframes and evaluating drivers..."):
        auto_tf=auto_timeframes(asset)
        auto_drv=auto_drivers(asset,style)

    available = [
        tf for tf in TIMEFRAMES
        if auto_tf[tf].get("available", auto_tf[tf].get("bars",0) >= 55)
    ]
    missing = [tf for tf in TIMEFRAMES if tf not in available]

    essential = STYLE_EXEC_TFS[style]
    essential_available = [tf for tf in essential if tf in available]

    # Hard-stop only when the selected trading horizon genuinely lacks enough
    # usable structure. Missing low-weight TFs no longer kill the whole analysis.
    enough_for_style = (
        len(available) >= 4
        and len(essential_available) >= max(2, len(essential)//2)
    )

    if not enough_for_style:
        st.error(
            "The development market-data feed still does not have enough usable "
            "history for this trading horizon."
        )

        diag_rows = []
        for tf in TIMEFRAMES:
            d = auto_tf[tf]
            diag_rows.append({
                "Timeframe": tf,
                "Bars": d.get("bars",0),
                "Status": "Available" if tf in available else "Insufficient",
                "Source": d.get("source",""),
                "Latest": d.get("last_timestamp","Unavailable"),
            })
        st.dataframe(pd.DataFrame(diag_rows), use_container_width=True, hide_index=True)

        st.caption(
            "This table shows exactly which timeframe failed. If most rows show "
            "0 bars, the hosted Yahoo development feed is being blocked/rate-limited "
            "rather than the analysis logic failing."
        )

        if st.button("Retry Market Data", key="premium_retry_market_data"):
            st.cache_data.clear()
            st.rerun()
        return

    if missing:
        st.warning(
            "Degraded data mode: "
            + ", ".join(missing)
            + " could not be classified with enough bars. Margin Manor will "
              "renormalize the timeframe weights across the available data instead "
              "of treating missing data as neutral evidence."
        )

    tf,drv=apply_overrides(auto_tf,auto_drv)
    r=analyze(asset,style,session,tf,drv)
    confirm,weaken=confirm_lists(r)
    bias_cls="positive" if r["bias_dir"]>0 else "negative" if r["bias_dir"]<0 else "neutral"; ready_cls="positive" if r["readiness_score"]>=70 else "neutral" if r["readiness_score"]>=45 else "negative"; driver_cls="positive" if r["driver_score"]>0.15 else "negative" if r["driver_score"]<-0.15 else "neutral"
    now=datetime.now(ZoneInfo("Asia/Singapore")).strftime("%d %b %Y · %H:%M:%S SGT")
    st.markdown('<div class="section-title">2. AUTOMATIC MARKET READ</div>',unsafe_allow_html=True)
    _html(f'''<div class="premium-score-grid"><div class="insight-score-card {bias_cls}"><span>DIRECTIONAL BIAS</span><strong>{r['bias']}</strong><small>Automatic price + driver thesis</small></div><div class="insight-score-card {ready_cls}"><span>EXECUTION READINESS</span><strong>{r['readiness']}</strong><small>{r['readiness_score']}% relevant-TF alignment</small></div><div class="insight-score-card neutral"><span>CONFLUENCE</span><strong>{r['strength']} / 100</strong><small>Agreement score, not win probability</small></div><div class="insight-score-card {driver_cls}"><span>DATA COVERAGE</span><strong>{r['price_coverage']}% Price</strong><small>{r['driver_coverage']}% driver observations available</small></div></div><div class="premium-freshness"><span>ANALYSIS GENERATED</span><strong>{now}</strong><small>Source timestamps appear below.</small></div>''')
    if r.get("session_meta"):
        sm=r["session_meta"]; cls="positive" if sm["direction"]>0 else "negative" if sm["direction"]<0 else "neutral"; _html(f'<div class="session-tape-card"><span>{session.upper()} SESSION TAPE</span><strong class="{cls}">{sm["state"]}</strong><p>{sm["change_pct"]:+.2f}% from session open · {sm["date"]} · {sm["bars"]} five-minute bars</p></div>')

    st.markdown('<div class="section-title">3. 9-TIMEFRAME AUTO CLASSIFICATION</div>',unsafe_allow_html=True)
    rows="";
    for t in TIMEFRAMES:
        d=tf[t]
        cls="positive" if d["state"]=="Bullish" else "negative" if d["state"]=="Bearish" else "neutral"
        status = "Proxy" if d.get("proxy") else "Live/Recent" if d.get("available") else "Insufficient"
        rows+=f'<tr><td><strong>{t}</strong><br><small>{status}</small></td><td class="{cls}">{d["state"]}</td><td>{d.get("score",0):+.2f}</td><td>{d.get("structure","")}</td><td>{d.get("trend","")}</td><td>{d.get("momentum","")}</td></tr>'
    _html(f'<div class="insight-panel"><div class="insight-table-scroll premium-table-scroll"><table class="insight-table"><thead><tr><th>TF</th><th>Auto Read</th><th>Score</th><th>Structure</th><th>Trend</th><th>Momentum</th></tr></thead><tbody>{rows}</tbody></table></div></div>')

    st.markdown('<div class="section-title">4. AUTOMATIC DRIVER ANALYSIS</div>',unsafe_allow_html=True)
    rows="";
    for x in drv:
        cls="positive" if x["weighted_effect"]>0 else "negative" if x["weighted_effect"]<0 else "neutral"; rows+=f'<tr><td><strong>{x["name"]}</strong></td><td>{x["input"]}</td><td>{x["tier"]}</td><td class="{cls}">{x["impact"]}</td><td>{x["source"]}</td><td>{x["freshness"]}</td></tr>'
    _html(f'<div class="insight-panel"><div class="insight-table-scroll premium-table-scroll"><table class="insight-table"><thead><tr><th>Driver</th><th>Auto State</th><th>Tier</th><th>Effect</th><th>Source</th><th>Latest</th></tr></thead><tbody>{rows}</tbody></table></div></div>')

    st.markdown('<div class="section-title">5. COMPREHENSIVE MEMBER INSIGHT</div>',unsafe_allow_html=True)
    _html(f'<div class="analysis-prose-grid"><div class="analysis-prose-card"><span>AUTOMATIC PRICE & TIMEFRAME STRUCTURE</span><p>{structure_narrative(r)}</p></div><div class="analysis-prose-card"><span>{style.upper()} INTERPRETATION</span><p>The engine weights the nine timeframes according to the selected trading horizon rather than counting bullish versus bearish labels equally.</p></div><div class="analysis-prose-card full"><span>AUTOMATIC DRIVER INTERPRETATION</span><p>{driver_narrative(r)}</p></div></div>')

    st.markdown('<div class="section-title">6. MEMBER TRADING CONCLUSION</div>',unsafe_allow_html=True)
    sub="Do not force a buy or sell thesis." if r["bias_dir"]==0 else "Preferred direction and execution structure are substantially aligned." if r["readiness_score"]>=70 else "A preferred direction exists, but execution confirmation is still required."
    ch="".join(f"<li>{x}</li>" for x in confirm); wh="".join(f"<li>{x}</li>" for x in weaken)
    sess="" if not r.get("session_meta") else f'<p><strong>Session:</strong> {session} tape is {r["session_meta"]["state"].lower()} ({r["session_meta"]["change_pct"]:+.2f}% from session open); it affects readiness but does not dominate the core model.</p>'
    _html(f'''<div class="trading-conclusion {bias_cls}"><div class="conclusion-top"><div><span>MEMBER LIVE ENGINE · {style.upper()}{' · '+session.upper() if session!='Not session-specific' else ''}</span><h2>{r['bias']}</h2><p>{sub}</p></div><div class="conclusion-score"><small>CONFLUENCE</small><strong>{r['strength']}</strong><span>/100</span></div></div><div class="conclusion-reason"><h3>Why Margin Manor reaches this conclusion</h3><p>{conclusion_reason(r)}</p><p><strong>Automatic price read:</strong> {r['lt']} long-term · {r['ht']} higher-TF · {r['intraday']} intraday · {r['execution']} execution.</p><p><strong>Automatic drivers:</strong> {r['driver_environment']} with a score of {r['driver_strength']:+d}. The driver environment is directly included in the conclusion.</p>{sess}</div><div class="conclusion-columns"><div><h3>What strengthens the preferred setup</h3><ul>{ch}</ul></div><div><h3>What weakens or invalidates it</h3><ul>{wh}</ul></div></div><div class="conclusion-disclaimer">Structured decision support only. Automatic classifications can be wrong, data can be delayed or unavailable, and driver relationships can change across regimes.</div></div>''')

    with st.expander("Audit: how Margin Manor classified the market"):
        st.write("Each timeframe uses a deterministic model: **45% swing structure, 35% EMA trend, 20% momentum**. Trader-style weights are applied afterward.")
        st.write("Drivers use observable market/FRED proxies with explicit source labels. The engine does not invent unavailable policy expectations; for example, US 2Y is labelled a policy-rate proxy.")
        st.write("Manual Override changes the final calculation only when the member explicitly enables it.")
    if st.button("Sign out of Member Access", key="premium_bottom_signout"):
        supabase_logout()
        st.session_state["_mm_active_page"] = "Home"
        st.rerun()
