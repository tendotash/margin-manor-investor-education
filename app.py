import streamlit as st
import json
from pathlib import Path
from datetime import date
from textwrap import dedent
import re

st.set_page_config(
    page_title="Margin Manor | Investor Education",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)


BASE_DIR = Path(__file__).resolve().parent

def load_css():
    css_file = BASE_DIR / "assets" / "style.css"

    with open(css_file, "r", encoding="utf-8") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

load_css()

def render_html(markup):
    """Render custom HTML directly, without Markdown re-parsing it."""
    st.html(dedent(markup).strip())



def tradingview_widget(script_src, config, height=360, container_class="mm-tv-widget"):
    """Render an official TradingView embed inside Streamlit."""
    config_json = json.dumps(config)
    widget_html = f"""
    <div class="{container_class}">
        <div class="tradingview-widget-container" style="height:{height}px;width:100%;">
            <div class="tradingview-widget-container__widget" style="height:100%;width:100%;"></div>
            <script type="text/javascript" src="{script_src}" async>
            {config_json}
            </script>
        </div>
    </div>
    """
    try:
        st.html(
            dedent(widget_html).strip(),
            width="stretch",
            unsafe_allow_javascript=True
        )
    except TypeError:
        # Compatibility fallback if Streamlit is older than the JS-enabled st.html API.
        from streamlit.components.v1 import html as components_html
        components_html(
            dedent(widget_html).strip(),
            height=height,
            scrolling=False
        )


def live_economic_calendar(height=360, compact=False):
    """Live economic releases and central-bank events."""
    countries = (
        "us,eu,gb,cn,jp,au,ca"
        if compact
        else "ar,au,br,ca,cn,fr,de,in,id,it,jp,kr,mx,ru,sa,za,tr,gb,us,eu"
    )
    importance = "0,1" if compact else "-1,0,1"
    tradingview_widget(
        "https://s3.tradingview.com/external-embedding/embed-widget-events.js",
        {
            "colorTheme": "dark",
            "isTransparent": True,
            "locale": "en",
            "countryFilter": countries,
            "importanceFilter": importance,
            "width": "100%",
            "height": max(height - 2, 250),
        },
        height=height,
        container_class="mm-live-calendar",
    )


def live_ticker_tape(height=78):
    """Live multi-asset prices and daily changes."""
    tradingview_widget(
        "https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js",
        {
            "symbols": [
                {"proName": "OANDA:XAUUSD", "title": "Gold"},
                {"proName": "TVC:DXY", "title": "DXY"},
                {"proName": "FOREXCOM:SPXUSD", "title": "S&P 500"},
                {"proName": "TVC:US10Y", "title": "US 10Y"},
                {"proName": "BITSTAMP:BTCUSD", "title": "Bitcoin"},
                {"proName": "FX:EURUSD", "title": "EUR/USD"},
                {"proName": "FX:USDJPY", "title": "USD/JPY"},
            ],
            "showSymbolLogo": False,
            "isTransparent": True,
            "displayMode": "adaptive",
            "colorTheme": "dark",
            "locale": "en",
        },
        height=height,
        container_class="mm-live-ticker",
    )


def live_top_stories(height=430, symbol=None):
    """Live TradingView market-news brief."""
    config = {
        "feedMode": "all_symbols" if not symbol else "symbol",
        "isTransparent": True,
        "displayMode": "regular",
        "width": "100%",
        "height": max(height - 2, 280),
        "colorTheme": "dark",
        "locale": "en",
    }
    if symbol:
        config["symbol"] = symbol

    tradingview_widget(
        "https://s3.tradingview.com/external-embedding/embed-widget-timeline.js",
        config,
        height=height,
        container_class="mm-live-news",
    )


def live_market_overview(height=520, forex_only=False):
    """Live macro/FX market overview with current prices and daily changes."""
    if forex_only:
        tabs = [
            {
                "title": "Major FX",
                "symbols": [
                    {"s": "FX_IDC:EURUSD", "d": "EUR / USD"},
                    {"s": "FX_IDC:GBPUSD", "d": "GBP / USD"},
                    {"s": "FX_IDC:USDJPY", "d": "USD / JPY"},
                    {"s": "FX_IDC:USDCHF", "d": "USD / CHF"},
                    {"s": "FX_IDC:AUDUSD", "d": "AUD / USD"},
                    {"s": "FX_IDC:USDCAD", "d": "USD / CAD"},
                ],
                "originalTitle": "Major FX",
            }
        ]
        title = "FX Market"
    else:
        tabs = [
            {
                "title": "Macro",
                "symbols": [
                    {"s": "OANDA:XAUUSD", "d": "Gold"},
                    {"s": "TVC:DXY", "d": "US Dollar Index"},
                    {"s": "FOREXCOM:SPXUSD", "d": "S&P 500"},
                    {"s": "NASDAQ:NDX", "d": "Nasdaq 100"},
                    {"s": "TVC:US10Y", "d": "US 10Y Yield"},
                    {"s": "TVC:VIX", "d": "VIX"},
                ],
                "originalTitle": "Macro",
            },
            {
                "title": "FX",
                "symbols": [
                    {"s": "FX_IDC:EURUSD", "d": "EUR / USD"},
                    {"s": "FX_IDC:GBPUSD", "d": "GBP / USD"},
                    {"s": "FX_IDC:USDJPY", "d": "USD / JPY"},
                    {"s": "FX_IDC:AUDUSD", "d": "AUD / USD"},
                ],
                "originalTitle": "FX",
            },
            {
                "title": "Crypto",
                "symbols": [
                    {"s": "BITSTAMP:BTCUSD", "d": "Bitcoin"},
                    {"s": "BITSTAMP:ETHUSD", "d": "Ethereum"},
                ],
                "originalTitle": "Crypto",
            },
        ]
        title = "Global Markets"

    tradingview_widget(
        "https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js",
        {
            "colorTheme": "dark",
            "dateRange": "1D",
            "showChart": True,
            "locale": "en",
            "largeChartUrl": "",
            "isTransparent": True,
            "showSymbolLogo": True,
            "showFloatingTooltip": False,
            "width": "100%",
            "height": max(height - 2, 320),
            "title": title,
            "tabs": tabs,
        },
        height=height,
        container_class="mm-live-overview",
    )


def live_gold_overview(height=500):
    """Live XAUUSD quote and chart."""
    tradingview_widget(
        "https://s3.tradingview.com/external-embedding/embed-widget-symbol-overview.js",
        {
            "symbols": [["Gold|OANDA:XAUUSD|1D"]],
            "chartOnly": False,
            "width": "100%",
            "height": max(height - 2, 320),
            "locale": "en",
            "colorTheme": "dark",
            "autosize": False,
            "showVolume": False,
            "showMA": False,
            "hideDateRanges": False,
            "hideMarketStatus": False,
            "hideSymbolLogo": False,
            "scalePosition": "right",
            "scaleMode": "Normal",
            "fontFamily": "Inter, Arial, sans-serif",
            "fontSize": "10",
            "noTimeScale": False,
            "valuesTracking": "1",
            "changeMode": "price-and-percent",
            "chartType": "area",
            "lineWidth": 2,
            "lineType": 0,
        },
        height=height,
        container_class="mm-live-gold",
    )


# ============================================================
# MARGIN MANOR INSIGHT ENGINE
# ============================================================

TIMEFRAME_ORDER = ["Monthly", "Weekly", "Daily", "H4", "H1", "M30", "M15", "M5", "M1"]
DIRECTION_VALUE = {"Bullish": 1.0, "Neutral": 0.0, "Bearish": -1.0}

STYLE_TF_WEIGHTS = {
    "Scalper": {
        "Monthly": 0.00, "Weekly": 0.00, "Daily": 0.03, "H4": 0.05,
        "H1": 0.10, "M30": 0.12, "M15": 0.20, "M5": 0.28, "M1": 0.22,
    },
    "Day Trader": {
        "Monthly": 0.03, "Weekly": 0.05, "Daily": 0.12, "H4": 0.18,
        "H1": 0.22, "M30": 0.17, "M15": 0.12, "M5": 0.08, "M1": 0.03,
    },
    "Session Trader": {
        "Monthly": 0.02, "Weekly": 0.04, "Daily": 0.10, "H4": 0.16,
        "H1": 0.22, "M30": 0.20, "M15": 0.14, "M5": 0.08, "M1": 0.04,
    },
    "Swing Trader": {
        "Monthly": 0.10, "Weekly": 0.22, "Daily": 0.30, "H4": 0.20,
        "H1": 0.10, "M30": 0.05, "M15": 0.02, "M5": 0.01, "M1": 0.00,
    },
}

STYLE_PRICE_DRIVER_WEIGHTS = {
    "Scalper": (0.80, 0.20),
    "Day Trader": (0.68, 0.32),
    "Session Trader": (0.62, 0.38),
    "Swing Trader": (0.58, 0.42),
}

STYLE_EXECUTION_TFS = {
    "Scalper": ["M15", "M5", "M1"],
    "Day Trader": ["H4", "H1", "M30", "M15", "M5"],
    "Session Trader": ["H1", "M30", "M15", "M5", "M1"],
    "Swing Trader": ["Weekly", "Daily", "H4", "H1"],
}


def _driver(name, tier, weight, states, note):
    return {
        "name": name,
        "tier": tier,
        "weight": float(weight),
        "states": states,
        "note": note,
    }


ASSET_DRIVER_CONFIG = {
    "XAUUSD — Gold": [
        _driver(
            "DXY / US Dollar", "Primary", 1.20,
            {"Bullish": -1.0, "Neutral": 0.0, "Bearish": 1.0},
            "A stronger USD is typically a headwind for dollar-priced gold; a weaker USD is typically supportive."
        ),
        _driver(
            "US Real Yields", "Primary", 1.30,
            {"Rising": -1.0, "Neutral": 0.0, "Falling": 1.0},
            "Higher real yields raise the opportunity cost of holding non-yielding gold; falling real yields are typically supportive."
        ),
        _driver(
            "US 10Y Yield", "Primary", 1.05,
            {"Rising": -1.0, "Neutral": 0.0, "Falling": 1.0},
            "Rising Treasury yields can pressure gold; falling yields can provide a tailwind."
        ),
        _driver(
            "Fed Expectations", "Primary", 1.15,
            {"Hawkish": -1.0, "Neutral": 0.0, "Dovish": 1.0},
            "More hawkish rate expectations are generally a gold headwind; more dovish expectations are generally supportive."
        ),
        _driver(
            "Silver / XAGUSD", "Confirmation", 0.65,
            {"Bullish": 0.8, "Neutral": 0.0, "Bearish": -0.8},
            "Silver strength or weakness can confirm or contradict broader precious-metals momentum."
        ),
        _driver(
            "VIX / Risk Stress", "Context", 0.45,
            {"Rising": 0.45, "Neutral": 0.0, "Falling": -0.25},
            "Rising stress can support safe-haven demand, although the relationship is contextual rather than mechanical."
        ),
        _driver(
            "Oil", "Context", 0.35,
            {"Bullish": 0.35, "Neutral": 0.0, "Bearish": -0.20},
            "Oil can affect inflation expectations and macro risk; it is a secondary gold driver rather than a primary one."
        ),
        _driver(
            "Inflation Expectations", "Macro", 0.55,
            {"Rising": 0.55, "Neutral": 0.0, "Falling": -0.30},
            "Rising inflation expectations can be supportive for gold, but real yields and policy expectations still matter."
        ),
    ],

    "EURUSD": [
        _driver(
            "DXY / US Dollar", "Primary", 1.25,
            {"Bullish": -1.0, "Neutral": 0.0, "Bearish": 1.0},
            "EURUSD commonly moves inversely to broad USD strength."
        ),
        _driver(
            "Fed Expectations", "Primary", 1.10,
            {"Hawkish": -1.0, "Neutral": 0.0, "Dovish": 1.0},
            "A more hawkish Fed generally supports USD and pressures EURUSD."
        ),
        _driver(
            "ECB Expectations", "Primary", 1.10,
            {"Hawkish": 1.0, "Neutral": 0.0, "Dovish": -1.0},
            "A more hawkish ECB generally supports EUR relative to USD."
        ),
        _driver(
            "US 2Y Yield", "Rates", 0.90,
            {"Rising": -1.0, "Neutral": 0.0, "Falling": 1.0},
            "Higher short-dated US yields can strengthen USD relative to EUR."
        ),
        _driver(
            "German 2Y Yield", "Rates", 0.90,
            {"Rising": 1.0, "Neutral": 0.0, "Falling": -1.0},
            "Higher euro-area front-end yields can support EUR."
        ),
        _driver(
            "US–Euro Rate Differential", "Primary", 1.05,
            {"US Advantage Widening": -1.0, "Neutral": 0.0, "Euro Advantage Widening": 1.0},
            "The relative rate advantage between the US and euro area is a core EURUSD macro input."
        ),
        _driver(
            "European Growth Outlook", "Macro", 0.55,
            {"Improving": 0.65, "Neutral": 0.0, "Weakening": -0.65},
            "Improving euro-area growth can support EUR; weakening growth can weigh on it."
        ),
    ],

    "GBPUSD": [
        _driver(
            "DXY / US Dollar", "Primary", 1.20,
            {"Bullish": -1.0, "Neutral": 0.0, "Bearish": 1.0},
            "Broad USD strength is typically a headwind for GBPUSD."
        ),
        _driver(
            "Fed Expectations", "Primary", 1.05,
            {"Hawkish": -1.0, "Neutral": 0.0, "Dovish": 1.0},
            "A more hawkish Fed tends to support USD relative to GBP."
        ),
        _driver(
            "BoE Expectations", "Primary", 1.05,
            {"Hawkish": 1.0, "Neutral": 0.0, "Dovish": -1.0},
            "A more hawkish Bank of England tends to support GBP."
        ),
        _driver(
            "US 2Y Yield", "Rates", 0.85,
            {"Rising": -1.0, "Neutral": 0.0, "Falling": 1.0},
            "Higher US front-end yields can support USD and pressure GBPUSD."
        ),
        _driver(
            "UK 2Y Gilt Yield", "Rates", 0.85,
            {"Rising": 1.0, "Neutral": 0.0, "Falling": -1.0},
            "Higher UK front-end yields can support GBP relative to USD."
        ),
        _driver(
            "UK Growth Outlook", "Macro", 0.55,
            {"Improving": 0.65, "Neutral": 0.0, "Weakening": -0.65},
            "Improving UK growth expectations can support sterling."
        ),
        _driver(
            "Risk Sentiment", "Context", 0.35,
            {"Risk-On": 0.35, "Neutral": 0.0, "Risk-Off": -0.35},
            "Sterling can behave as a pro-cyclical currency, so severe risk-off conditions may be a headwind."
        ),
    ],

    "USDJPY": [
        _driver(
            "US 10Y Yield", "Primary", 1.15,
            {"Rising": 1.0, "Neutral": 0.0, "Falling": -1.0},
            "Higher US yields can widen the rate advantage over Japan and support USDJPY."
        ),
        _driver(
            "US 2Y Yield", "Primary", 1.05,
            {"Rising": 1.0, "Neutral": 0.0, "Falling": -1.0},
            "US front-end yields are important for the USD side of the rate differential."
        ),
        _driver(
            "Japan 10Y Yield", "Primary", 1.00,
            {"Rising": -1.0, "Neutral": 0.0, "Falling": 1.0},
            "Higher Japanese yields can support JPY and pressure USDJPY."
        ),
        _driver(
            "Fed Expectations", "Primary", 1.00,
            {"Hawkish": 1.0, "Neutral": 0.0, "Dovish": -1.0},
            "A more hawkish Fed generally supports USDJPY through the USD/rates channel."
        ),
        _driver(
            "BoJ Expectations", "Primary", 1.10,
            {"Hawkish": -1.0, "Neutral": 0.0, "Dovish": 1.0},
            "A more hawkish BoJ can support JPY and pressure USDJPY."
        ),
        _driver(
            "Risk Sentiment", "Context", 0.55,
            {"Risk-On": 0.55, "Neutral": 0.0, "Risk-Off": -0.75},
            "Risk-off conditions can strengthen JPY through safe-haven flows."
        ),
        _driver(
            "DXY / US Dollar", "Confirmation", 0.60,
            {"Bullish": 0.65, "Neutral": 0.0, "Bearish": -0.65},
            "Broad USD direction can confirm or contradict the USD side of USDJPY."
        ),
    ],

    "NAS100 — Nasdaq 100": [
        _driver(
            "US 10Y Yield", "Primary", 1.15,
            {"Rising": -1.0, "Neutral": 0.0, "Falling": 1.0},
            "Higher long-term yields can pressure growth-stock valuations; falling yields are typically supportive."
        ),
        _driver(
            "US Real Yields", "Primary", 1.15,
            {"Rising": -1.0, "Neutral": 0.0, "Falling": 1.0},
            "Higher real discount rates can be a headwind for long-duration growth equities."
        ),
        _driver(
            "Fed Expectations", "Primary", 1.05,
            {"Hawkish": -1.0, "Neutral": 0.0, "Dovish": 1.0},
            "More dovish policy expectations can support growth equities through the rates channel."
        ),
        _driver(
            "VIX", "Primary", 1.00,
            {"Rising": -1.0, "Neutral": 0.0, "Falling": 1.0},
            "Rising implied volatility usually coincides with greater equity stress."
        ),
        _driver(
            "Semiconductor Strength", "Confirmation", 0.80,
            {"Bullish": 0.85, "Neutral": 0.0, "Bearish": -0.85},
            "Semiconductors are an important leadership group for the Nasdaq complex."
        ),
        _driver(
            "S&P 500", "Confirmation", 0.65,
            {"Bullish": 0.65, "Neutral": 0.0, "Bearish": -0.65},
            "Broad equity participation can confirm or contradict Nasdaq direction."
        ),
        _driver(
            "Market Breadth", "Confirmation", 0.75,
            {"Improving": 0.80, "Neutral": 0.0, "Weakening": -0.80},
            "Improving breadth suggests participation is expanding rather than relying on a small number of leaders."
        ),
        _driver(
            "DXY / US Dollar", "Context", 0.35,
            {"Bullish": -0.35, "Neutral": 0.0, "Bearish": 0.35},
            "A very strong USD can tighten financial conditions and pressure multinational earnings, but this is secondary."
        ),
    ],

    "SPX500 — S&P 500": [
        _driver(
            "US 10Y Yield", "Primary", 1.00,
            {"Rising": -0.85, "Neutral": 0.0, "Falling": 0.85},
            "Higher yields can tighten financial conditions and pressure equity valuations."
        ),
        _driver(
            "Fed Expectations", "Primary", 1.00,
            {"Hawkish": -1.0, "Neutral": 0.0, "Dovish": 1.0},
            "More accommodative policy expectations are generally supportive for equities."
        ),
        _driver(
            "VIX", "Primary", 1.15,
            {"Rising": -1.0, "Neutral": 0.0, "Falling": 1.0},
            "Rising volatility is typically a headwind for the broad equity market."
        ),
        _driver(
            "Credit Spreads", "Primary", 1.05,
            {"Widening": -1.0, "Neutral": 0.0, "Tightening": 1.0},
            "Widening credit spreads signal greater stress; tightening spreads are generally supportive."
        ),
        _driver(
            "Earnings Expectations", "Macro", 0.85,
            {"Improving": 0.90, "Neutral": 0.0, "Weakening": -0.90},
            "Improving earnings expectations support equity fundamentals."
        ),
        _driver(
            "Market Breadth", "Confirmation", 0.80,
            {"Improving": 0.85, "Neutral": 0.0, "Weakening": -0.85},
            "Broad participation strengthens the quality of an index move."
        ),
        _driver(
            "DXY / US Dollar", "Context", 0.30,
            {"Bullish": -0.30, "Neutral": 0.0, "Bearish": 0.30},
            "A very strong USD can tighten financial conditions and pressure multinational earnings."
        ),
    ],

    "BTCUSD — Bitcoin": [
        _driver(
            "DXY / US Dollar", "Primary", 1.00,
            {"Bullish": -0.85, "Neutral": 0.0, "Bearish": 0.85},
            "Broad USD strength can be a liquidity headwind for Bitcoin; a weaker USD can be supportive."
        ),
        _driver(
            "US Real Yields", "Primary", 0.95,
            {"Rising": -0.85, "Neutral": 0.0, "Falling": 0.85},
            "Rising real yields can tighten financial conditions and pressure speculative assets."
        ),
        _driver(
            "Global Liquidity", "Primary", 1.20,
            {"Expanding": 1.0, "Neutral": 0.0, "Contracting": -1.0},
            "Expanding liquidity is generally supportive for risk assets, including Bitcoin."
        ),
        _driver(
            "Nasdaq / Growth Stocks", "Confirmation", 0.75,
            {"Bullish": 0.75, "Neutral": 0.0, "Bearish": -0.75},
            "Bitcoin often shares a risk/liquidity regime with growth equities."
        ),
        _driver(
            "Crypto ETF / Institutional Flows", "Primary", 1.00,
            {"Inflows": 1.0, "Neutral": 0.0, "Outflows": -1.0},
            "Sustained institutional inflows or outflows can materially affect Bitcoin demand."
        ),
        _driver(
            "Crypto Market Breadth", "Confirmation", 0.70,
            {"Improving": 0.75, "Neutral": 0.0, "Weakening": -0.75},
            "Improving breadth can confirm a healthier crypto risk environment."
        ),
        _driver(
            "Risk Sentiment", "Context", 0.55,
            {"Risk-On": 0.60, "Neutral": 0.0, "Risk-Off": -0.60},
            "Bitcoin often benefits from risk-on liquidity conditions and can struggle during sharp deleveraging."
        ),
    ],

    "WTI Crude Oil": [
        _driver(
            "DXY / US Dollar", "Primary", 0.80,
            {"Bullish": -0.70, "Neutral": 0.0, "Bearish": 0.70},
            "A stronger USD can be a headwind for dollar-priced commodities."
        ),
        _driver(
            "US Crude Inventories", "Primary", 1.00,
            {"Building": -1.0, "Neutral": 0.0, "Drawing": 1.0},
            "Inventory builds can signal softer balances; draws can signal tighter balances."
        ),
        _driver(
            "OPEC+ Supply Stance", "Primary", 1.15,
            {"Increasing Supply": -1.0, "Neutral": 0.0, "Cutting Supply": 1.0},
            "Supply increases are typically bearish for oil; production cuts are typically supportive."
        ),
        _driver(
            "Global Growth Outlook", "Primary", 0.95,
            {"Improving": 0.90, "Neutral": 0.0, "Weakening": -0.90},
            "Stronger global growth generally improves expected oil demand."
        ),
        _driver(
            "China Demand", "Primary", 1.00,
            {"Improving": 1.0, "Neutral": 0.0, "Weakening": -1.0},
            "China is a major source of global commodity demand."
        ),
        _driver(
            "Geopolitical Supply Risk", "Context", 0.70,
            {"Rising": 0.80, "Neutral": 0.0, "Falling": -0.30},
            "Rising supply-disruption risk can add an oil risk premium."
        ),
        _driver(
            "Risk Sentiment", "Context", 0.35,
            {"Risk-On": 0.35, "Neutral": 0.0, "Risk-Off": -0.35},
            "Broad risk sentiment can influence oil through growth expectations and positioning."
        ),
    ],
}



# ============================================================
# V6 — UNIVERSAL PAIR DRIVER ENGINE
# ============================================================

CURRENCY_META = {
    "USD": {"name": "US Dollar", "central_bank": "Fed", "risk_beta": 0.10},
    "EUR": {"name": "Euro", "central_bank": "ECB", "risk_beta": 0.10},
    "GBP": {"name": "British Pound", "central_bank": "BoE", "risk_beta": 0.25},
    "JPY": {"name": "Japanese Yen", "central_bank": "BoJ", "risk_beta": -0.90},
    "CHF": {"name": "Swiss Franc", "central_bank": "SNB", "risk_beta": -0.75},
    "CAD": {"name": "Canadian Dollar", "central_bank": "BoC", "risk_beta": 0.55, "commodity": "Oil"},
    "AUD": {"name": "Australian Dollar", "central_bank": "RBA", "risk_beta": 0.75, "commodity": "China / Industrial Commodities"},
    "NZD": {"name": "New Zealand Dollar", "central_bank": "RBNZ", "risk_beta": 0.70, "commodity": "Global Growth / Commodities"},
    "NOK": {"name": "Norwegian Krone", "central_bank": "Norges Bank", "risk_beta": 0.55, "commodity": "Oil"},
    "SEK": {"name": "Swedish Krona", "central_bank": "Riksbank", "risk_beta": 0.40},
    "SGD": {"name": "Singapore Dollar", "central_bank": "MAS", "risk_beta": 0.20},
    "CNH": {"name": "Offshore Chinese Yuan", "central_bank": "PBoC", "risk_beta": 0.35},
    "CNY": {"name": "Chinese Yuan", "central_bank": "PBoC", "risk_beta": 0.35},
    "HKD": {"name": "Hong Kong Dollar", "central_bank": "HKMA", "risk_beta": 0.05},
    "MXN": {"name": "Mexican Peso", "central_bank": "Banxico", "risk_beta": 0.80, "commodity": "Oil / US Growth"},
    "ZAR": {"name": "South African Rand", "central_bank": "SARB", "risk_beta": 0.90, "commodity": "Metals / China"},
    "TRY": {"name": "Turkish Lira", "central_bank": "CBRT", "risk_beta": 1.00},
    "PLN": {"name": "Polish Zloty", "central_bank": "NBP", "risk_beta": 0.45},
    "CZK": {"name": "Czech Koruna", "central_bank": "CNB", "risk_beta": 0.40},
    "HUF": {"name": "Hungarian Forint", "central_bank": "MNB", "risk_beta": 0.65},
    "DKK": {"name": "Danish Krone", "central_bank": "Danmarks Nationalbank", "risk_beta": 0.05},
    "INR": {"name": "Indian Rupee", "central_bank": "RBI", "risk_beta": 0.45, "commodity": "Oil"},
    "BRL": {"name": "Brazilian Real", "central_bank": "BCB", "risk_beta": 0.80, "commodity": "Commodities / China"},
    "KRW": {"name": "South Korean Won", "central_bank": "BoK", "risk_beta": 0.65, "commodity": "Global Technology / Trade"},
    "TWD": {"name": "Taiwan Dollar", "central_bank": "CBC", "risk_beta": 0.50, "commodity": "Global Technology / Semiconductors"},
    "IDR": {"name": "Indonesian Rupiah", "central_bank": "Bank Indonesia", "risk_beta": 0.55, "commodity": "Commodities"},
    "MYR": {"name": "Malaysian Ringgit", "central_bank": "BNM", "risk_beta": 0.50, "commodity": "Oil / China"},
    "THB": {"name": "Thai Baht", "central_bank": "BoT", "risk_beta": 0.40},
    "PHP": {"name": "Philippine Peso", "central_bank": "BSP", "risk_beta": 0.45},
    "AED": {"name": "UAE Dirham", "central_bank": "CBUAE", "risk_beta": 0.05, "commodity": "Oil"},
    "SAR": {"name": "Saudi Riyal", "central_bank": "SAMA", "risk_beta": 0.05, "commodity": "Oil"},
}

SPECIAL_MARKET_ALIASES = {
    "NAS100": "NAS100 — Nasdaq 100",
    "NASDAQ": "NAS100 — Nasdaq 100",
    "USTEC": "NAS100 — Nasdaq 100",
    "NDX": "NAS100 — Nasdaq 100",
    "SPX500": "SPX500 — S&P 500",
    "SP500": "SPX500 — S&P 500",
    "US500": "SPX500 — S&P 500",
    "SPX": "SPX500 — S&P 500",
    "BTCUSD": "BTCUSD — Bitcoin",
    "BTC": "BTCUSD — Bitcoin",
    "WTI": "WTI Crude Oil",
    "USOIL": "WTI Crude Oil",
    "CL": "WTI Crude Oil",
}

QUICK_PAIR_EXAMPLES = [
    "XAUUSD", "XAGUSD",
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD",
    "EURGBP", "EURJPY", "EURCHF", "EURCAD", "EURAUD", "EURNZD",
    "GBPJPY", "GBPCHF", "GBPCAD", "GBPAUD", "GBPNZD",
    "AUDJPY", "AUDCHF", "AUDCAD", "AUDNZD",
    "NZDJPY", "NZDCHF", "NZDCAD",
    "CADJPY", "CADCHF", "CHFJPY",
]


def normalize_asset_code(raw):
    value = (raw or "").upper().strip()
    value = value.split(".")[0]
    value = value.split("#")[0]
    value = re.sub(r"[^A-Z0-9]", "", value)

    aliases = {
        "GOLD": "XAUUSD",
        "SILVER": "XAGUSD",
        "XAU": "XAUUSD",
        "XAG": "XAGUSD",
    }
    return aliases.get(value, value)


def _currency_label(code):
    meta = CURRENCY_META.get(code, {})
    return meta.get("name", code)


def _central_bank_label(code):
    meta = CURRENCY_META.get(code, {})
    return meta.get("central_bank", f"{code} Central Bank")


def _risk_effect_for_pair(base, quote):
    base_beta = CURRENCY_META.get(base, {}).get("risk_beta", 0.0)
    quote_beta = CURRENCY_META.get(quote, {}).get("risk_beta", 0.0)
    diff = base_beta - quote_beta

    if abs(diff) < 0.20:
        return None

    risk_on_effect = max(-1.0, min(1.0, diff))
    return {
        "Risk-On": risk_on_effect,
        "Neutral": 0.0,
        "Risk-Off": -risk_on_effect,
    }


def _commodity_driver_for_currency(currency, role):
    meta = CURRENCY_META.get(currency, {})
    commodity = meta.get("commodity")
    if not commodity:
        return None

    direction = 1.0 if role == "base" else -1.0
    return _driver(
        f"{currency} Commodity Link — {commodity}",
        "Context",
        0.45,
        {
            "Bullish / Improving": 0.55 * direction,
            "Neutral": 0.0,
            "Bearish / Weakening": -0.55 * direction,
        },
        f"{currency} has a meaningful relationship with {commodity.lower()}. "
        f"Strength in that theme can support {currency}; weakness can pressure it. "
        f"Because {currency} is the {role} currency in this pair, the effect is translated into the pair direction."
    )


def build_forex_pair_drivers(pair):
    base, quote = pair[:3], pair[3:6]
    base_cb = _central_bank_label(base)
    quote_cb = _central_bank_label(quote)

    drivers = [
        _driver(
            f"{base_cb} Expectations ({base})", "Primary", 1.05,
            {"Hawkish": 1.0, "Neutral": 0.0, "Dovish": -1.0},
            f"A more hawkish {base_cb} generally supports the base currency {base} and therefore supports {pair}."
        ),
        _driver(
            f"{quote_cb} Expectations ({quote})", "Primary", 1.05,
            {"Hawkish": -1.0, "Neutral": 0.0, "Dovish": 1.0},
            f"A more hawkish {quote_cb} generally supports the quote currency {quote}, which tends to pressure {pair}."
        ),
        _driver(
            f"{base} 2Y Yield", "Rates", 0.90,
            {"Rising": 1.0, "Neutral": 0.0, "Falling": -1.0},
            f"Rising front-end yields in {base} can improve the relative rate support for the base currency."
        ),
        _driver(
            f"{quote} 2Y Yield", "Rates", 0.90,
            {"Rising": -1.0, "Neutral": 0.0, "Falling": 1.0},
            f"Rising front-end yields in {quote} can strengthen the quote currency and pressure the pair."
        ),
        _driver(
            f"{base}–{quote} Rate Differential", "Primary", 1.20,
            {
                f"{base} Advantage Widening": 1.0,
                "Neutral": 0.0,
                f"{quote} Advantage Widening": -1.0,
            },
            f"The relative rate advantage between {base} and {quote} is one of the most important generic macro inputs for {pair}."
        ),
        _driver(
            f"{base} Growth / Economic Surprises", "Macro", 0.60,
            {"Improving": 0.65, "Neutral": 0.0, "Weakening": -0.65},
            f"Improving relative growth or data surprises can support {base}, the base currency."
        ),
        _driver(
            f"{quote} Growth / Economic Surprises", "Macro", 0.60,
            {"Improving": -0.65, "Neutral": 0.0, "Weakening": 0.65},
            f"Improving relative growth or data surprises can support {quote}, which is usually a headwind for {pair}."
        ),
    ]

    # Broad USD confirmation when USD is one side of the pair.
    if base == "USD":
        drivers.append(
            _driver(
                "DXY / Broad US Dollar", "Confirmation", 0.70,
                {"Bullish": 0.75, "Neutral": 0.0, "Bearish": -0.75},
                f"Broad USD strength generally confirms upside in {pair} when USD is the base currency."
            )
        )
    elif quote == "USD":
        drivers.append(
            _driver(
                "DXY / Broad US Dollar", "Confirmation", 0.70,
                {"Bullish": -0.75, "Neutral": 0.0, "Bearish": 0.75},
                f"Broad USD strength generally pressures {pair} when USD is the quote currency."
            )
        )

    # Pair-specific risk sentiment effect.
    risk_states = _risk_effect_for_pair(base, quote)
    if risk_states:
        drivers.append(
            _driver(
                "Global Risk Sentiment", "Context", 0.50,
                risk_states,
                f"Risk sentiment is translated through the relative risk sensitivity of {base} versus {quote}. "
                "This is contextual and can change across market regimes."
            )
        )

    # Commodity-linked currency overlays.
    base_commodity = _commodity_driver_for_currency(base, "base")
    quote_commodity = _commodity_driver_for_currency(quote, "quote")
    if base_commodity:
        drivers.append(base_commodity)
    if quote_commodity and (not base_commodity or quote_commodity["name"] != base_commodity["name"]):
        drivers.append(quote_commodity)

    return drivers


def build_metal_pair_drivers(pair):
    metal, quote = pair[:3], pair[3:6]
    metal_name = "Gold" if metal == "XAU" else "Silver"
    quote_cb = _central_bank_label(quote)

    drivers = [
        _driver(
            "US Real Yields", "Primary", 1.25,
            {"Rising": -1.0, "Neutral": 0.0, "Falling": 1.0},
            f"Real yields are a major global macro input for precious metals. Falling real yields are typically supportive for {metal_name}."
        ),
        _driver(
            "US 10Y Yield", "Primary", 0.95,
            {"Rising": -0.85, "Neutral": 0.0, "Falling": 0.85},
            f"Falling Treasury yields can support {metal_name}; rising yields can be a headwind."
        ),
        _driver(
            "Fed Expectations", "Primary", 1.00,
            {"Hawkish": -1.0, "Neutral": 0.0, "Dovish": 1.0},
            f"More dovish Fed expectations are generally supportive for {metal_name}; hawkish expectations can be a headwind."
        ),
        _driver(
            "DXY / Broad US Dollar", "Primary", 0.85,
            {"Bullish": -0.80, "Neutral": 0.0, "Bearish": 0.80},
            f"Broad USD direction can influence global precious-metals pricing even when {metal_name} is quoted in {quote}."
        ),
        _driver(
            f"{quote} Currency Strength", "Primary", 1.00,
            {"Bullish": -1.0, "Neutral": 0.0, "Bearish": 1.0},
            f"Because {metal_name} is quoted in {quote}, a stronger {quote} tends to pressure {pair}, while a weaker {quote} tends to support it."
        ),
        _driver(
            f"{quote_cb} Expectations ({quote})", "Rates", 0.75,
            {"Hawkish": -0.75, "Neutral": 0.0, "Dovish": 0.75},
            f"A more hawkish {quote_cb} can support the quote currency and therefore act as a headwind for {pair}."
        ),
        _driver(
            f"{quote} 2Y Yield", "Rates", 0.70,
            {"Rising": -0.70, "Neutral": 0.0, "Falling": 0.70},
            f"Rising yields in the quote currency can strengthen {quote} and pressure {pair}."
        ),
        _driver(
            "VIX / Risk Stress", "Context", 0.40,
            {"Rising": 0.40, "Neutral": 0.0, "Falling": -0.20},
            f"Rising risk stress can support safe-haven demand for {metal_name}, but the relationship is contextual."
        ),
    ]

    if metal == "XAU":
        drivers.append(
            _driver(
                "Silver / Precious-Metals Confirmation", "Confirmation", 0.55,
                {"Bullish": 0.60, "Neutral": 0.0, "Bearish": -0.60},
                "Silver strength can confirm broader precious-metals demand; divergence can reduce conviction."
            )
        )
    else:
        drivers.append(
            _driver(
                "Gold / Precious-Metals Confirmation", "Confirmation", 0.60,
                {"Bullish": 0.65, "Neutral": 0.0, "Bearish": -0.65},
                "Gold strength can confirm broader precious-metals demand and help contextualize silver."
            )
        )

    return drivers


def get_asset_driver_config(asset):
    """Return a driver set for presets, any FX pair, or XAU/XAG against any currency."""
    normalized = normalize_asset_code(asset)

    # Preserve the dedicated non-FX market profiles from V5.
    special = SPECIAL_MARKET_ALIASES.get(normalized)
    if special and special in ASSET_DRIVER_CONFIG:
        return special, ASSET_DRIVER_CONFIG[special], "special"

    # Accept any six-character pair, including currencies not explicitly listed.
    if len(normalized) == 6 and normalized.isalpha():
        base, quote = normalized[:3], normalized[3:6]

        if base in {"XAU", "XAG"}:
            return normalized, build_metal_pair_drivers(normalized), "metal"

        # Treat all other 3+3 symbols as a currency pair. Known currencies get richer
        # labels/overlays; unknown currencies still work through the generic pair framework.
        return normalized, build_forex_pair_drivers(normalized), "forex"

    # Fallback to XAUUSD rather than failing the whole page.
    return "XAUUSD", build_metal_pair_drivers("XAUUSD"), "metal"


def describe_pair(asset):
    normalized = normalize_asset_code(asset)
    if len(normalized) == 6 and normalized.isalpha():
        base, quote = normalized[:3], normalized[3:6]
        if base in {"XAU", "XAG"}:
            metal_name = "Gold" if base == "XAU" else "Silver"
            return (
                f"{normalized}: {metal_name} is the base asset and {quote} is the quote currency. "
                f"Drivers that strengthen {metal_name} support the pair; drivers that strengthen {quote} tend to pressure the pair."
            )

        return (
            f"{normalized}: {_currency_label(base)} ({base}) is the base currency and "
            f"{_currency_label(quote)} ({quote}) is the quote currency. "
            f"Base-currency strength supports the pair; quote-currency strength pressures it."
        )

    return "The selected symbol uses a dedicated market-driver profile."

def _weighted_average(values, weights):
    total_weight = sum(weights)
    if total_weight <= 0:
        return 0.0
    return sum(v * w for v, w in zip(values, weights)) / total_weight


def _state_from_score(score, strong=0.45):
    if score >= strong:
        return "Bullish"
    if score <= -strong:
        return "Bearish"
    return "Mixed / Neutral"


def _tone_class(score):
    if score > 0.15:
        return "positive"
    if score < -0.15:
        return "negative"
    return "neutral"


def _driver_environment(score):
    if score >= 0.60:
        return "Strong Tailwind"
    if score >= 0.20:
        return "Supportive"
    if score <= -0.60:
        return "Strong Headwind"
    if score <= -0.20:
        return "Adverse"
    return "Mixed / Neutral"


def _effect_label(effect, weight):
    magnitude = abs(effect) * weight
    if effect > 0:
        return "Strong Tailwind" if magnitude >= 0.90 else "Tailwind"
    if effect < 0:
        return "Strong Headwind" if magnitude >= 0.90 else "Headwind"
    return "Neutral"


def _group_score(tf_inputs, names):
    vals = [DIRECTION_VALUE[tf_inputs[n]] for n in names]
    return sum(vals) / len(vals)


def analyze_market_insight(asset, trader_style, session, tf_inputs, driver_inputs):
    tf_weights = STYLE_TF_WEIGHTS[trader_style]
    price_score = sum(DIRECTION_VALUE[tf_inputs[tf]] * tf_weights[tf] for tf in TIMEFRAME_ORDER)

    driver_rows = []
    driver_weighted_sum = 0.0
    driver_total_weight = 0.0

    _, active_drivers, _ = get_asset_driver_config(asset)

    for driver in active_drivers:
        selected = driver_inputs[driver["name"]]
        effect = driver["states"][selected]
        weighted_effect = effect * driver["weight"]
        driver_weighted_sum += weighted_effect
        driver_total_weight += driver["weight"]

        driver_rows.append({
            "name": driver["name"],
            "tier": driver["tier"],
            "input": selected,
            "effect": effect,
            "weight": driver["weight"],
            "weighted_effect": weighted_effect,
            "impact": _effect_label(effect, driver["weight"]),
            "note": driver["note"],
        })

    driver_score = driver_weighted_sum / driver_total_weight if driver_total_weight else 0.0

    price_weight, driver_weight = STYLE_PRICE_DRIVER_WEIGHTS[trader_style]
    combined_score = (price_score * price_weight) + (driver_score * driver_weight)

    if combined_score >= 0.20:
        bias = "LOOK FOR BUYS"
        bias_direction = 1
    elif combined_score <= -0.20:
        bias = "LOOK FOR SELLS"
        bias_direction = -1
    else:
        bias = "WAIT / NO CLEAR EDGE"
        bias_direction = 0

    long_term_score = _group_score(tf_inputs, ["Monthly", "Weekly"])
    higher_score = _group_score(tf_inputs, ["Daily", "H4"])
    intraday_score = _group_score(tf_inputs, ["H1", "M30"])
    execution_score = _weighted_average(
        [DIRECTION_VALUE[tf_inputs["M15"]], DIRECTION_VALUE[tf_inputs["M5"]], DIRECTION_VALUE[tf_inputs["M1"]]],
        [0.40, 0.40, 0.20]
    )

    relevant_tfs = STYLE_EXECUTION_TFS[trader_style]
    if bias_direction == 0:
        readiness = "WAIT — BIAS NOT CLEAR"
        readiness_score = 0
    else:
        aligned = 0.0
        total = 0.0
        for tf in relevant_tfs:
            val = DIRECTION_VALUE[tf_inputs[tf]]
            total += 1.0
            if val == bias_direction:
                aligned += 1.0
            elif val == 0:
                aligned += 0.35

        readiness_score = round(100 * aligned / total) if total else 0

        # Penalize strong macro/price conflict.
        price_driver_conflict = (price_score * driver_score) < -0.18
        if readiness_score >= 70 and not price_driver_conflict:
            readiness = "FAVOR SETUPS — ALIGNMENT PRESENT"
        elif readiness_score >= 45:
            readiness = "WAIT FOR CONFIRMATION"
        else:
            readiness = "LOW READINESS — STRUCTURAL CONFLICT"

    strength_score = round(abs(combined_score) * 100)
    price_strength = round(price_score * 100)
    driver_strength = round(driver_score * 100)

    return {
        "asset": asset,
        "trader_style": trader_style,
        "session": session,
        "tf_inputs": tf_inputs,
        "driver_rows": driver_rows,
        "price_score": price_score,
        "driver_score": driver_score,
        "combined_score": combined_score,
        "price_strength": price_strength,
        "driver_strength": driver_strength,
        "strength_score": strength_score,
        "bias": bias,
        "bias_direction": bias_direction,
        "readiness": readiness,
        "readiness_score": readiness_score,
        "long_term_score": long_term_score,
        "higher_score": higher_score,
        "intraday_score": intraday_score,
        "execution_score": execution_score,
        "long_term_state": _state_from_score(long_term_score),
        "higher_state": _state_from_score(higher_score),
        "intraday_state": _state_from_score(intraday_score),
        "execution_state": _state_from_score(execution_score, strong=0.25),
        "driver_environment": _driver_environment(driver_score),
    }


def _structure_narrative(result):
    lt = result["long_term_state"]
    ht = result["higher_state"]
    intra = result["intraday_state"]
    exe = result["execution_state"]

    sentences = []

    if lt == "Bullish" and ht == "Bearish":
        sentences.append(
            "The Monthly and Weekly structure is bullish, while Daily and H4 are bearish. "
            "That combination is consistent with a higher-timeframe correction occurring inside a broader bullish structure."
        )
    elif lt == "Bearish" and ht == "Bullish":
        sentences.append(
            "The Monthly and Weekly structure is bearish, while Daily and H4 are bullish. "
            "That suggests a medium-term rally or reversal attempt inside a broader bearish backdrop."
        )
    elif lt == ht and lt != "Mixed / Neutral":
        sentences.append(
            f"The broader and higher-timeframe structure are aligned {lt.lower()}, which gives the market a clearer structural direction."
        )
    else:
        sentences.append(
            "The higher timeframes are not fully synchronized, so the market should be treated as structurally mixed rather than cleanly trending."
        )

    if intra == "Bullish" and exe == "Bullish":
        sentences.append("Intraday and execution timeframes are aligned bullish, showing short-term upside agreement.")
    elif intra == "Bearish" and exe == "Bearish":
        sentences.append("Intraday and execution timeframes are aligned bearish, showing short-term downside agreement.")
    elif intra != exe:
        sentences.append(
            f"Intraday structure is {intra.lower()} while execution structure is {exe.lower()}, "
            "so the immediate move is not fully aligned with the surrounding intraday context."
        )
    else:
        sentences.append("Intraday and execution structure remain mixed, which reduces immediate directional clarity.")

    return " ".join(sentences)


def _style_narrative(result):
    style = result["trader_style"]
    session = result["session"]
    tf = result["tf_inputs"]

    if style == "Scalper":
        return (
            f"For a scalper, M15/M5/M1 carry the greatest execution importance. "
            f"Current execution reads M15 {tf['M15'].lower()}, M5 {tf['M5'].lower()} and M1 {tf['M1'].lower()}. "
            "Higher timeframes are used mainly as context rather than as the immediate trigger."
        )
    if style == "Day Trader":
        return (
            f"For a day trader, Daily/H4 establish the tradable backdrop while H1/M30/M15 refine the intraday direction. "
            f"Here H4 is {tf['H4'].lower()}, H1 is {tf['H1'].lower()} and M30 is {tf['M30'].lower()}, "
            "so the day-trading conclusion gives more weight to these frames than to Monthly or M1."
        )
    if style == "Session Trader":
        return (
            f"For a {session} session trader, H1/M30 provide session context and M15/M5/M1 provide execution confirmation. "
            f"The engine therefore emphasizes whether those intraday frames are aligning during {session}, "
            "while Daily/H4 remain directional context."
        )
    return (
        f"For a swing trader, Weekly/Daily/H4 dominate the decision. "
        f"Weekly is {tf['Weekly'].lower()}, Daily is {tf['Daily'].lower()} and H4 is {tf['H4'].lower()}; "
        "lower timeframes are treated mainly as timing tools rather than reasons to reverse a swing thesis."
    )


def _driver_narrative(result):
    positive = sorted(
        [r for r in result["driver_rows"] if r["weighted_effect"] > 0],
        key=lambda r: abs(r["weighted_effect"]),
        reverse=True
    )
    negative = sorted(
        [r for r in result["driver_rows"] if r["weighted_effect"] < 0],
        key=lambda r: abs(r["weighted_effect"]),
        reverse=True
    )

    parts = [f"The driver environment is classified as {result['driver_environment'].lower()} for {result['asset']}."]
    if positive:
        p = ", ".join(f"{r['name']} ({r['input']})" for r in positive[:3])
        parts.append(f"The strongest supportive inputs are {p}.")
    if negative:
        n = ", ".join(f"{r['name']} ({r['input']})" for r in negative[:3])
        parts.append(f"The main opposing inputs are {n}.")
    if not positive and not negative:
        parts.append("The selected drivers are neutral, so price structure is doing most of the analytical work.")
    return " ".join(parts)


def _confirmation_lists(result):
    direction = result["bias_direction"]
    tf = result["tf_inputs"]
    style = result["trader_style"]
    relevant = STYLE_EXECUTION_TFS[style]

    confirm = []
    weaken = []

    if direction == 0:
        confirm.append("Wait for price structure to develop a clearer directional majority on the timeframes most relevant to the selected trading style.")
        confirm.append("Wait for the primary asset drivers to shift from mixed toward a common tailwind or headwind.")
        weaken.append("Avoid forcing a directional thesis while price and drivers remain balanced.")
        return confirm, weaken

    desired = "Bullish" if direction > 0 else "Bearish"
    opposite = "Bearish" if direction > 0 else "Bullish"

    for tf_name in relevant:
        if tf[tf_name] != desired:
            confirm.append(f"{tf_name} turns {desired.lower()} to align with the preferred direction.")

    supportive = [r for r in result["driver_rows"] if r["weighted_effect"] * direction > 0]
    opposing = [r for r in result["driver_rows"] if r["weighted_effect"] * direction < 0]

    if supportive:
        for row in sorted(supportive, key=lambda r: abs(r["weighted_effect"]), reverse=True)[:2]:
            confirm.append(f"{row['name']} remains {row['input'].lower()}, preserving a {row['impact'].lower()}.")

    if opposing:
        for row in sorted(opposing, key=lambda r: abs(r["weighted_effect"]), reverse=True)[:2]:
            weaken.append(f"{row['name']} remains {row['input'].lower()}, which is currently a {row['impact'].lower()}.")

    for tf_name in relevant[:3]:
        if tf[tf_name] == desired:
            weaken.append(f"{tf_name} flips {opposite.lower()}, weakening the current {desired.lower()} alignment.")

    # Keep the UI concise and remove duplicate text.
    confirm = list(dict.fromkeys(confirm))[:5]
    weaken = list(dict.fromkeys(weaken))[:5]
    return confirm, weaken


def _bias_explanation(result):
    if result["bias_direction"] == 0:
        return (
            "Price structure and the selected drivers do not produce enough directional separation to justify a buy-side or sell-side preference. "
            "The appropriate conclusion is to wait for alignment rather than manufacture a trade."
        )

    direction_word = "buy" if result["bias_direction"] > 0 else "sell"
    price_same_direction = result["price_score"] * result["bias_direction"] > 0.10
    drivers_same_direction = result["driver_score"] * result["bias_direction"] > 0.10

    if price_same_direction and drivers_same_direction:
        return (
            f"The {direction_word}-side preference is supported by both the style-weighted timeframe structure and the driver environment. "
            "That agreement makes the directional thesis stronger than a conclusion based on timeframe counting alone."
        )
    if price_same_direction and not drivers_same_direction:
        return (
            f"The {direction_word}-side preference is being led by price structure, but the driver environment is not fully confirming it. "
            "This reduces conviction and makes execution confirmation more important."
        )
    if drivers_same_direction and not price_same_direction:
        return (
            f"The {direction_word}-side preference is being led by the macro/cross-asset drivers, while price structure remains conflicted. "
            "The engine therefore treats the thesis as conditional until the relevant execution timeframes begin to realign."
        )
    return (
        "The combined score is only marginally directional and contains meaningful conflict. "
        "Treat the preferred side as conditional rather than as an immediate entry signal."
    )


def insight_engine_page():
    top_ticker()

    render_html("""
    <div class="insight-hero">
        <div>
            <div class="insight-kicker">FREE MARKET TOOLS / INSIGHTS</div>
            <h1>Margin Manor Insight Engine</h1>
            <p>
                Read your own charts first, then enter what you see. Margin Manor combines
                multi-timeframe structure, dynamically generated pair-specific drivers, trading horizon
                and session context into one structured directional thesis.
            </p>
        </div>
        <div class="insight-method">
            <span>YOU PROVIDE</span>
            <strong>Chart observations + driver views</strong>
            <span>MARGIN MANOR PROVIDES</span>
            <strong>Alignment, conflicts, bias & confirmation conditions</strong>
        </div>
    </div>
    """)

    st.caption(
        "Supports any 6-character FX pair plus XAU/XAG metal pairs. The tool organizes the observations you enter; it does not read your chart automatically and its confluence score is not a probability of profit."
    )

    st.markdown('<div class="section-title">1. ANALYSIS PROFILE</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1.35, 1, 1], gap="medium")
    with c1:
        pair_mode = st.selectbox(
            "Asset Input",
            ["Enter Any Pair", "Quick Examples", "Other Market"],
            key="insight_asset_mode",
            help="Enter any 6-character FX pair such as EURUSD, GBPJPY, AUDCAD or an XAU/XAG metal pair such as XAUJPY."
        )

        if pair_mode == "Enter Any Pair":
            raw_asset = st.text_input(
                "Pair / Symbol",
                value="XAUUSD",
                key="insight_custom_pair",
                placeholder="e.g. EURUSD, GBPJPY, AUDCAD, XAUJPY",
            )
        elif pair_mode == "Quick Examples":
            raw_asset = st.selectbox(
                "Pair",
                QUICK_PAIR_EXAMPLES,
                key="insight_quick_pair",
            )
        else:
            raw_asset = st.selectbox(
                "Other Market",
                ["NAS100", "SPX500", "BTCUSD", "WTI"],
                key="insight_other_market",
            )

        asset, drivers, asset_kind = get_asset_driver_config(raw_asset)

    with c2:
        trader_style = st.selectbox(
            "Trading Style",
            ["Scalper", "Day Trader", "Session Trader", "Swing Trader"],
            index=1,
            key="insight_style"
        )
    with c3:
        if trader_style == "Session Trader":
            session = st.selectbox(
                "Trading Session",
                ["Asia", "London", "New York AM", "New York PM"],
                key="insight_session_required"
            )
        else:
            session = st.selectbox(
                "Session Context",
                ["Not session-specific", "Asia", "London", "New York AM", "New York PM"],
                key="insight_session_optional",
                help="Optional context for scalpers, day traders and swing traders."
            )

    st.markdown('<div class="section-title">2. YOUR 9-TIMEFRAME READ</div>', unsafe_allow_html=True)
    st.caption("Choose Bullish, Bearish or Neutral based on your own chart analysis.")

    tf_inputs = {}
    tf_columns = st.columns(3, gap="medium")
    tf_groups = [
        ("STRUCTURAL", ["Monthly", "Weekly", "Daily"]),
        ("INTRADAY", ["H4", "H1", "M30"]),
        ("EXECUTION", ["M15", "M5", "M1"]),
    ]

    for col, (label, frames) in zip(tf_columns, tf_groups):
        with col:
            render_html(f'<div class="input-panel-title">{label}</div>')
            for tf_name in frames:
                tf_inputs[tf_name] = st.selectbox(
                    tf_name,
                    ["Bullish", "Neutral", "Bearish"],
                    index=1,
                    key=f"insight_tf_{tf_name}",
                )

    st.markdown('<div class="section-title">3. DYNAMIC PAIR-SPECIFIC DRIVERS</div>', unsafe_allow_html=True)

    render_html(f"""
    <div class="pair-logic-card">
        <span>PAIR LOGIC</span>
        <strong>{asset}</strong>
        <p>{describe_pair(asset)}</p>
    </div>
    """)

    st.caption(
        f"Margin Manor generated {len(drivers)} drivers for {asset}. "
        "Primary drivers receive more analytical weight than rates, macro, confirmation and context drivers."
    )

    driver_inputs = {}
    driver_cols = st.columns(2, gap="large")

    for i, driver in enumerate(drivers):
        with driver_cols[i % 2]:
            options = list(driver["states"].keys())
            neutral_index = next(
                (idx for idx, opt in enumerate(options) if opt in {"Neutral"}),
                0
            )
            driver_inputs[driver["name"]] = st.selectbox(
                f"{driver['name']} · {driver['tier']}",
                options,
                index=neutral_index,
                key=f"insight_driver_{re.sub(r'[^A-Za-z0-9]', '_', asset)}_{re.sub(r'[^A-Za-z0-9]', '_', driver['name'])}",
                help=driver["note"]
            )

    action_col, reset_col = st.columns([1, 4])
    with action_col:
        if st.button("Analyze Confluence", type="primary", use_container_width=True):
            st.session_state["insight_show_result"] = True
    with reset_col:
        st.caption("After the first analysis, results update as you change the inputs.")

    if not st.session_state.get("insight_show_result", False):
        render_html("""
        <div class="insight-empty">
            <div class="insight-empty-icon">◎</div>
            <div>
                <strong>Ready when you are.</strong>
                <span>Complete the timeframe and driver inputs, then click Analyze Confluence.</span>
            </div>
        </div>
        """)
        return

    result = analyze_market_insight(asset, trader_style, session, tf_inputs, driver_inputs)
    confirm, weaken = _confirmation_lists(result)

    bias_class = (
        "positive" if result["bias_direction"] > 0
        else "negative" if result["bias_direction"] < 0
        else "neutral"
    )
    readiness_class = (
        "positive" if result["readiness_score"] >= 70
        else "neutral" if result["readiness_score"] >= 45
        else "negative"
    )
    driver_class = _tone_class(result["driver_score"])

    st.markdown('<div class="section-title">4. MARGIN MANOR ANALYSIS</div>', unsafe_allow_html=True)

    render_html(f"""
    <div class="insight-score-grid">
        <div class="insight-score-card {bias_class}">
            <span>DIRECTIONAL BIAS</span>
            <strong>{result['bias']}</strong>
            <small>Combined price + driver thesis</small>
        </div>
        <div class="insight-score-card {readiness_class}">
            <span>EXECUTION READINESS</span>
            <strong>{result['readiness']}</strong>
            <small>{result['readiness_score']}% relevant-TF alignment</small>
        </div>
        <div class="insight-score-card neutral">
            <span>CONFLUENCE STRENGTH</span>
            <strong>{result['strength_score']} / 100</strong>
            <small>Directional agreement, not win probability</small>
        </div>
        <div class="insight-score-card {driver_class}">
            <span>DRIVER ENVIRONMENT</span>
            <strong>{result['driver_environment']}</strong>
            <small>Driver score {result['driver_strength']:+d}</small>
        </div>
    </div>
    """)

    # Structure matrix
    structure_rows = [
        ("Long-Term", "Monthly + Weekly", result["long_term_state"], result["long_term_score"]),
        ("Higher TF", "Daily + H4", result["higher_state"], result["higher_score"]),
        ("Intraday", "H1 + M30", result["intraday_state"], result["intraday_score"]),
        ("Execution", "M15 + M5 + M1", result["execution_state"], result["execution_score"]),
    ]

    structure_html = ""
    for layer, frames, state, score in structure_rows:
        cls = _tone_class(score)
        structure_html += f"""
        <tr>
            <td>{layer}</td>
            <td>{frames}</td>
            <td class="{cls}">{state}</td>
            <td>{round(score * 100):+d}</td>
        </tr>
        """

    left, right = st.columns([1.05, 1], gap="medium")
    with left:
        render_html(f"""
        <div class="insight-panel">
            <div class="insight-panel-heading">PRICE STRUCTURE</div>
            <table class="insight-table">
                <thead><tr><th>Layer</th><th>Timeframes</th><th>Read</th><th>Score</th></tr></thead>
                <tbody>{structure_html}</tbody>
            </table>
            <div class="insight-panel-note">
                Style-weighted price score: <strong>{result['price_strength']:+d}</strong>
            </div>
        </div>
        """)

    with right:
        driver_rows_html = ""
        for row in result["driver_rows"]:
            cls = "positive" if row["weighted_effect"] > 0 else "negative" if row["weighted_effect"] < 0 else "neutral"
            driver_rows_html += f"""
            <tr>
                <td>{row['name']}</td>
                <td>{row['input']}</td>
                <td>{row['tier']}</td>
                <td class="{cls}">{row['impact']}</td>
            </tr>
            """
        render_html(f"""
        <div class="insight-panel">
            <div class="insight-panel-heading">DRIVER ANALYSIS</div>
            <div class="insight-table-scroll">
                <table class="insight-table">
                    <thead><tr><th>Driver</th><th>Your View</th><th>Tier</th><th>Asset Effect</th></tr></thead>
                    <tbody>{driver_rows_html}</tbody>
                </table>
            </div>
            <div class="insight-panel-note">
                Driver score: <strong>{result['driver_strength']:+d}</strong> · {result['driver_environment']}
            </div>
        </div>
        """)

    st.markdown('<div class="section-title">5. COMPREHENSIVE INSIGHT</div>', unsafe_allow_html=True)

    structure_text = _structure_narrative(result)
    style_text = _style_narrative(result)
    driver_text = _driver_narrative(result)
    bias_text = _bias_explanation(result)

    render_html(f"""
    <div class="analysis-prose-grid">
        <div class="analysis-prose-card">
            <span>PRICE & TIMEFRAME STRUCTURE</span>
            <p>{structure_text}</p>
        </div>
        <div class="analysis-prose-card">
            <span>TRADER-TYPE / SESSION INTERPRETATION</span>
            <p>{style_text}</p>
        </div>
        <div class="analysis-prose-card full">
            <span>DRIVER INTERPRETATION</span>
            <p>{driver_text}</p>
        </div>
    </div>
    """)

    st.markdown('<div class="section-title">6. TRADING CONCLUSION</div>', unsafe_allow_html=True)

    conclusion_title = result["bias"]
    if result["bias_direction"] == 0:
        conclusion_sub = "Do not force a buy or sell thesis."
    elif result["readiness_score"] >= 70:
        conclusion_sub = "Preferred direction and execution timeframes are substantially aligned."
    else:
        conclusion_sub = "Preferred direction is identified, but execution confirmation is still required."

    confirm_html = "".join(f"<li>{item}</li>" for item in confirm) or "<li>No additional confirmation conditions generated.</li>"
    weaken_html = "".join(f"<li>{item}</li>" for item in weaken) or "<li>No major weakening conditions generated.</li>"

    render_html(f"""
    <div class="trading-conclusion {bias_class}">
        <div class="conclusion-top">
            <div>
                <span>FOR {trader_style.upper()}{' · ' + session.upper() if session != 'Not session-specific' else ''}</span>
                <h2>{conclusion_title}</h2>
                <p>{conclusion_sub}</p>
            </div>
            <div class="conclusion-score">
                <small>CONFLUENCE</small>
                <strong>{result['strength_score']}</strong>
                <span>/100</span>
            </div>
        </div>

        <div class="conclusion-reason">
            <h3>Why Margin Manor reaches this conclusion</h3>
            <p>{bias_text}</p>
            <p>
                <strong>Price:</strong> {result['long_term_state']} long-term ·
                {result['higher_state']} higher-TF ·
                {result['intraday_state']} intraday ·
                {result['execution_state']} execution.
            </p>
            <p>
                <strong>Drivers:</strong> {result['driver_environment']} for {asset}
                with a driver score of {result['driver_strength']:+d}.
                The driver environment is included directly in the directional conclusion rather than being shown as a separate, unused dashboard.
            </p>
        </div>

        <div class="conclusion-columns">
            <div>
                <h3>What strengthens the preferred setup</h3>
                <ul>{confirm_html}</ul>
            </div>
            <div>
                <h3>What weakens or invalidates it</h3>
                <ul>{weaken_html}</ul>
            </div>
        </div>

        <div class="conclusion-disclaimer">
            Directional bias is not an instruction to enter immediately. Execution readiness is shown separately so a trader can distinguish
            “which side currently has better confluence” from “whether conditions are ready for a trade.”
        </div>
    </div>
    """)

    with st.expander("How this conclusion is weighted"):
        price_weight, driver_weight = STYLE_PRICE_DRIVER_WEIGHTS[trader_style]
        st.write(
            f"For **{trader_style}**, the combined directional thesis currently uses approximately "
            f"**{round(price_weight * 100)}% price/timeframe structure** and "
            f"**{round(driver_weight * 100)}% asset-specific drivers**."
        )
        st.write(
            "Within price structure, each of the nine timeframes is weighted differently according to the selected trading style. "
            "The engine does not simply count how many timeframes are bullish versus bearish."
        )
        st.write(
            "Driver weights also differ by importance. Primary drivers have more influence than context or confirmation drivers."
        )
        st.caption(
            "The framework is a structured decision-support model. Relationships between assets and macro drivers can change across market regimes."
        )


PAGES = [
    "Home",
    "About Margin Manor",
    "Who It Helps",
    "Free Market Tools / Insights",
    "Beginner Investing",
    "Stocks",
    "ETFs",
    "REITs",
    "Bonds",
    "Risk Management",
    "Market Briefs",
    "Margin Manor Terminal",
    "Strategy Library",
    "Economic Calendar",
    "Gold / FX Dashboard",
    "Ask a Question",
]

with st.sidebar:
    render_html("""
    <div class="sidebar-logo">
        <div class="logo-mark">M</div>
        <div class="logo-title">MARGIN MANOR</div>
        <div class="logo-sub">INVESTOR EDUCATION</div>
    </div>
    """)

    st.markdown('<div class="nav-section">MAIN</div>', unsafe_allow_html=True)
    page = st.radio(
        "Main",
        ["Home", "About Margin Manor", "Who It Helps", "Free Market Tools / Insights"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="nav-section">LEARN</div>', unsafe_allow_html=True)
    learn_page = st.radio(
        "Learn",
        ["Beginner Investing", "Stocks", "ETFs", "REITs", "Bonds", "Risk Management"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="nav-section">MARKET BRIEFS</div>', unsafe_allow_html=True)
    brief_page = st.radio("Briefs", ["Market Briefs"], label_visibility="collapsed")

    st.markdown('<div class="nav-section">TOOLS</div>', unsafe_allow_html=True)
    tool_page = st.radio(
        "Tools",
        ["Margin Manor Terminal", "Strategy Library", "Economic Calendar", "Gold / FX Dashboard"],
        label_visibility="collapsed"
    )

    st.markdown('<div class="nav-section">CONTACT</div>', unsafe_allow_html=True)
    contact_page = st.radio("Contact", ["Ask a Question"], label_visibility="collapsed")

    chosen = st.session_state.get("Main", page)
    for key in ["Learn", "Briefs", "Tools", "Contact"]:
        if key in st.session_state:
            chosen = st.session_state[key]

    # Streamlit radios in different groups can all hold values.
    # This manual override allows page links through query-like buttons later.
    page = chosen

    render_html("""
    <div class="sidebar-card">
        <div class="sidebar-card-title">MARGIN MANOR</div>
        <div class="sidebar-card-text">Price. Time. Discipline.<br>Master the process.</div>
        <br>
        <div style="color:#D9A441; letter-spacing:18px; padding-left:14px;">◎ ✕ ◇ ✉</div>
    </div>
    """)

def top_ticker():
    render_html("""
    <div class="live-feed-label">
        <span>LIVE MARKET FEED</span>
        <small>Prices and daily changes update automatically • provider timing may vary</small>
    </div>
    """)
    live_ticker_tape(height=78)


def tool_card(icon, title, text, link):
    return dedent(f"""
    <div class="tool-card">
        <div class="tool-icon">{icon}</div>
        <div class="tool-title">{title}</div>
        <div class="tool-text">{text}</div>
        <div class="tool-link">{link} →</div>
    </div>
    """).strip()

def home():
    top_ticker()

    render_html("""
    <div class="hero-grid">
        <div class="hero-left">
            <div class="welcome">Welcome to</div>
            <div class="main-title">MARGIN MANOR</div>
            <div class="subtitle">Investor Education. Tools. Insights.</div>
            <div class="hero-copy">
                Margin Manor is your home for clear, practical and time-tested investment knowledge.
                We break down the markets, asset classes and strategies — so you can build wealth
                with confidence and discipline.
            </div>
            <div class="button-row">
                <div class="fake-btn-primary">Explore Tools →</div>
                <div class="fake-btn-secondary">Browse Topics</div>
            </div>
        </div>

        <div class="hero-image">
            <div class="manor-building">
                <div class="roof"></div>
                <div class="pillar1"></div>
                <div class="pillar2"></div>
                <div class="pillar3"></div>
                <div class="pillar4"></div>
                <div class="steps"></div>
            </div>
            <div class="hero-quote">
                KNOWLEDGE BUILDS<br>CONFIDENCE.<br>
                <span>DISCIPLINE BUILDS WEALTH.</span>
            </div>
            <div class="hero-mini-logo">Ⓜ<br>MARGIN MANOR</div>
        </div>
    </div>
    """)

    st.markdown('<div class="section-title">QUICK ACCESS TOOLS</div>', unsafe_allow_html=True)
    tools_html = "".join([
        tool_card("▣", "Margin Manor Terminal", "Real-time market data, breadth, macro drivers, news and more.", "Launch Terminal"),
        tool_card("▱", "Strategy Library", "Explore proven strategies, frameworks and playbooks.", "View Library"),
        tool_card("▦", "Economic Calendar", "Track key economic events that move the markets.", "View Calendar"),
        tool_card("⌁", "Gold / FX Dashboard", "Live dashboard for Gold, Forex and key correlations.", "Open Dashboard"),
    ])
    render_html(f'<div class="tools-grid">{tools_html}</div>')

    st.markdown('<div class="section-title">LIVE MARKET BRIEF</div>', unsafe_allow_html=True)

    brief_col, events_col = st.columns([3.2, 1.25], gap="medium")

    with brief_col:
        render_html("""
        <div class="live-panel-heading">
            <div class="events-title">LATEST MARKET STORIES</div>
            <div class="live-events-sub">Live • automatically updated</div>
        </div>
        """)
        live_top_stories(height=330)

    with events_col:
        render_html("""
        <div class="live-events-heading">
            <div class="events-title">UPCOMING EVENTS</div>
            <div class="live-events-sub">Live • automatically updated</div>
        </div>
        """)
        live_economic_calendar(height=330, compact=True)

def content_page(title, subtitle, body):
    top_ticker()
    render_html(f"""
    <div class="content-card">
        <h2>{title}</h2>
        <p>{subtitle}</p>
    </div>
    <div class="content-card">
        {body}
    </div>
    """)

if page == "Home":
    home()

elif page == "About Margin Manor":
    content_page(
        "About Margin Manor",
        "Margin Manor is an investor education and market insights platform.",
        """
        <p>It helps beginners understand how markets move before risking money.</p>
        <ul>
            <li>Investor education</li>
            <li>Market briefs</li>
            <li>Macro and asset dashboards</li>
            <li>Risk management frameworks</li>
            <li>Strategy and research library</li>
        </ul>
        """
    )

elif page == "Who It Helps":
    content_page(
        "Who Margin Manor Helps",
        "Built for beginners, young investors, self-learners and market watchers.",
        """
        <ul>
            <li>People who want to start investing safely.</li>
            <li>People who want to understand stocks, ETFs, REITs and bonds.</li>
            <li>People who want simple market updates.</li>
            <li>People who want to learn risk before chasing returns.</li>
        </ul>
        """
    )

elif page == "Free Market Tools / Insights":
    insight_engine_page()

elif page == "Beginner Investing":
    content_page(
        "Beginner Investing",
        "Learn the foundation before choosing any product.",
        """
        <p>Investing means putting money into assets with the aim of growing wealth over time.</p>
        <ul>
            <li>Know your goal.</li>
            <li>Know your time horizon.</li>
            <li>Know your risk tolerance.</li>
            <li>Understand what you are buying.</li>
            <li>Do not invest money you urgently need.</li>
        </ul>
        """
    )

elif page == "Stocks":
    content_page(
        "Stocks",
        "A stock represents ownership in a company.",
        """
        <p>Stocks can grow through business expansion, price appreciation and dividends.</p>
        <ul>
            <li>Understand the company.</li>
            <li>Study revenue, profit and debt.</li>
            <li>Do not buy only because price is moving.</li>
            <li>Respect market and company-specific risk.</li>
        </ul>
        """
    )

elif page == "ETFs":
    content_page(
        "ETFs",
        "An ETF is a basket of assets traded like a stock.",
        """
        <p>ETFs are often beginner-friendly because they provide diversification through one product.</p>
        <ul>
            <li>Index ETFs</li>
            <li>Bond ETFs</li>
            <li>Sector ETFs</li>
            <li>Country ETFs</li>
            <li>Commodity ETFs</li>
        </ul>
        """
    )

elif page == "REITs":
    content_page(
        "REITs",
        "REITs give investors access to real estate income through listed markets.",
        """
        <p>REITs usually own income-generating properties such as malls, offices, warehouses, hotels or data centres.</p>
        <ul>
            <li>Distribution yield</li>
            <li>Occupancy rate</li>
            <li>Debt level</li>
            <li>Interest rate sensitivity</li>
        </ul>
        """
    )

elif page == "Bonds":
    content_page(
        "Bonds",
        "A bond is a loan from investors to a company or government.",
        """
        <p>Bonds usually pay interest and return principal at maturity, but they still carry risk.</p>
        <ul>
            <li>Coupon</li>
            <li>Maturity</li>
            <li>Yield</li>
            <li>Credit risk</li>
            <li>Duration risk</li>
        </ul>
        """
    )

elif page == "Risk Management":
    content_page(
        "Risk Management",
        "The goal is not only to make money. The goal is to survive long enough to compound.",
        """
        <ul>
            <li>Never risk money you cannot afford to lose.</li>
            <li>Diversify properly.</li>
            <li>Avoid emotional decisions.</li>
            <li>Understand worst-case scenarios.</li>
            <li>Protect capital first.</li>
        </ul>
        """
    )

elif page == "Market Briefs":
    top_ticker()
    render_html("""
    <div class="content-card">
        <h2>Live Market Briefs</h2>
        <p>
            Current market headlines and a live macro snapshot. This page updates automatically
            rather than relying on manually dated market commentary.
        </p>
    </div>
    """)
    news_col, macro_col = st.columns([1.15, 1], gap="medium")
    with news_col:
        live_top_stories(height=620)
    with macro_col:
        live_market_overview(height=620)

elif page == "Margin Manor Terminal":
    top_ticker()
    render_html("""
    <div class="content-card">
        <h2>Margin Manor Terminal</h2>
        <p>
            Live macro-market preview covering gold, equities, the dollar, yields, volatility,
            FX and crypto. Your separate full Margin Manor Terminal can be linked here later.
        </p>
    </div>
    """)
    live_market_overview(height=680)

elif page == "Strategy Library":
    content_page(
        "Strategy Library",
        "A structured library for your investing and trading frameworks.",
        """
        <ul>
            <li>Beginner ETF plan</li>
            <li>Dividend REIT watchlist</li>
            <li>Gold macro bias framework</li>
            <li>Risk checklist</li>
        </ul>
        """
    )

elif page == "Economic Calendar":
    top_ticker()
    render_html("""
    <div class="content-card economic-calendar-intro">
        <h2>Economic Calendar</h2>
        <p>
            Live upcoming macroeconomic releases, central-bank events and market-moving data.
            Use the filters inside the calendar to focus on the countries and event importance
            most relevant to your portfolio.
        </p>
    </div>
    """)
    live_economic_calendar(height=720, compact=False)

elif page == "Gold / FX Dashboard":
    top_ticker()
    render_html("""
    <div class="content-card">
        <h2>Gold / FX Dashboard</h2>
        <p>
            Live XAUUSD pricing, chart context and major-FX performance. Market data is supplied
            by TradingView and refreshes automatically.
        </p>
    </div>
    """)

    gold_col, fx_col = st.columns([1.05, 1], gap="medium")
    with gold_col:
        render_html("""
        <div class="live-panel-heading">
            <div class="events-title">GOLD — XAUUSD</div>
            <div class="live-events-sub">Live quote and chart</div>
        </div>
        """)
        live_gold_overview(height=550)

    with fx_col:
        render_html("""
        <div class="live-panel-heading">
            <div class="events-title">MAJOR FX</div>
            <div class="live-events-sub">Live prices and daily changes</div>
        </div>
        """)
        live_market_overview(height=550, forex_only=True)

    st.markdown('<div class="section-title">KEY MACRO EVENTS</div>', unsafe_allow_html=True)
    live_economic_calendar(height=520, compact=True)

elif page == "Ask a Question":
    top_ticker()
    render_html("""
    <div class="content-card">
        <h2>Ask a Question</h2>
        <p>Submit your investing question below.</p>
    </div>
    """)

    with st.form("contact_form"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        experience = st.selectbox("Investing experience", ["Beginner", "Some experience", "Intermediate", "Advanced"])
        question = st.text_area("Question")
        submitted = st.form_submit_button("Submit Question")

    if submitted:
        if not name or not email or not question:
            st.error("Please fill in your name, email and question.")
        else:
            st.info(
                "Your form is complete, but this site does not yet have a message destination configured. "
                "Connect an email, Google Sheet, Supabase table or webhook before publishing this form as a working submission."
            )
