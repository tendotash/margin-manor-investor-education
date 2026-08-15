import streamlit as st
import json
from pathlib import Path
from datetime import date
from textwrap import dedent

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
    home()

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
