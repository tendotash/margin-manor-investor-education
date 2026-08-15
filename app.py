import streamlit as st
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
    """Render indented multi-line HTML safely through Streamlit Markdown."""
    st.markdown(dedent(markup).strip(), unsafe_allow_html=True)

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
    <div class="top-ticker">
        <div class="ticker-item">
            <div class="ticker-symbol">XAUUSD</div>
            <div class="ticker-price">2,388.42</div>
            <div class="ticker-up">+12.63 (+0.53%)</div>
        </div>
        <div class="ticker-item">
            <div class="ticker-symbol">DXY</div>
            <div class="ticker-price">104.32</div>
            <div class="ticker-down">-0.28 (-0.27%)</div>
        </div>
        <div class="ticker-item">
            <div class="ticker-symbol">SPX500</div>
            <div class="ticker-price">5,447.87</div>
            <div class="ticker-up">+18.64 (+0.34%)</div>
        </div>
        <div class="ticker-item">
            <div class="ticker-symbol">US10Y</div>
            <div class="ticker-price">4.43%</div>
            <div class="ticker-down">-0.02 (-0.45%)</div>
        </div>
        <div class="ticker-item">
            <div class="ticker-symbol">BTCUSD</div>
            <div class="ticker-price">66,842.10</div>
            <div class="ticker-up">+731.45 (+1.11%)</div>
        </div>
        <div class="ticker-item">
            <div class="ticker-symbol">EURUSD</div>
            <div class="ticker-price">1.08871</div>
            <div class="ticker-down">-0.00231 (-0.21%)</div>
        </div>
        <div class="ticker-item">
            <div class="ticker-symbol">USDJPY</div>
            <div class="ticker-price">156.92</div>
            <div class="ticker-up">+0.21 (+0.13%)</div>
        </div>
        <div class="market-status">
            <div class="status-title">MARKET STATUS</div>
            <div class="status-value">● Risk-On</div>
        </div>
    </div>
    """)

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

    st.markdown('<div class="section-title">LATEST MARKET BRIEF</div>', unsafe_allow_html=True)
    render_html("""
    <div class="brief-grid">
        <div class="brief-card">
            <div class="brief-content">
                <div>
                    <div class="date-line">▣ 11 May 2025</div>
                    <div class="brief-headline">Weekly Market Brief – 11 May 2025</div>
                    <div class="brief-text">
                        Global markets ended the week mixed as investors weighed inflation data,
                        central bank signals and geopolitical tensions. Gold remains bid while
                        equities consolidate near highs.
                    </div>
                    <br>
                    <div class="tool-link">Read Full Brief →</div>
                </div>
                <div>
                    <table class="market-table">
                        <tr><th>ASSET</th><th>PRICE</th><th>CHANGE</th><th>TREND</th></tr>
                        <tr><td>XAUUSD</td><td>2,388.42</td><td class="ticker-up">+12.63</td><td>↑</td></tr>
                        <tr><td>SPX500</td><td>5,447.87</td><td class="ticker-up">+18.64</td><td>↑</td></tr>
                        <tr><td>DXY</td><td>104.32</td><td class="ticker-down">-0.28</td><td>↓</td></tr>
                        <tr><td>US10Y</td><td>4.43%</td><td class="ticker-down">-0.02</td><td>↓</td></tr>
                        <tr><td>BTCUSD</td><td>66,842.10</td><td class="ticker-up">+731.45</td><td>↑</td></tr>
                    </table>
                </div>
            </div>
        </div>

        <div class="events-card">
            <div class="events-title">UPCOMING EVENTS</div>
            <div class="event-item">
                <div class="event-date">13 May 2025 20:30</div>
                <div class="event-name">US CPI (MoM)</div>
            </div>
            <div class="event-item">
                <div class="event-date">14 May 2025 20:30</div>
                <div class="event-name">US PPI (MoM)</div>
            </div>
            <div class="event-item">
                <div class="event-date">15 May 2025 20:30</div>
                <div class="event-name">US Retail Sales (MoM)</div>
            </div>
            <div class="tool-link">View Full Calendar →</div>
        </div>
    </div>
    """)

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
    home()

elif page == "Margin Manor Terminal":
    content_page(
        "Margin Manor Terminal",
        "Your market command centre for macro, FX, gold and risk sentiment.",
        """
        <p>This section can later connect to your existing terminal.</p>
        <ul>
            <li>XAUUSD score</li>
            <li>Macro score</li>
            <li>Top market drivers</li>
            <li>USD, yields, VIX, oil and equities</li>
            <li>News and event tape</li>
        </ul>
        """
    )

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
    content_page(
        "Economic Calendar",
        "Track events that can move markets.",
        """
        <ul>
            <li>CPI and inflation data</li>
            <li>Jobs data</li>
            <li>Central bank meetings</li>
            <li>GDP releases</li>
            <li>PMI data</li>
            <li>Retail sales</li>
        </ul>
        """
    )

elif page == "Gold / FX Dashboard":
    content_page(
        "Gold / FX Dashboard",
        "Understand gold through USD, yields, risk sentiment and currency flows.",
        """
        <ul>
            <li>USD weak = often supportive for gold.</li>
            <li>Yields down = often supportive for gold.</li>
            <li>Risk-off = can support gold demand.</li>
            <li>Strong USD and rising yields can pressure gold.</li>
        </ul>
        """
    )

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
            st.success("Submitted. Next upgrade: connect this to Google Sheets, Supabase or email.")
