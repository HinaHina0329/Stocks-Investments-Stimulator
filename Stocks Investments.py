import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
import time
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="HinaHinaPro Pro Terminal",
    page_icon="🐂",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp {
        background-color: #1E222D;
        color: #FFFFFF;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #252A37;
        border-right: 1px solid #363C4E;
        color: #FFFFFF;
    }

    div.stButton > button {
        background-color: #343B4E !important;
        border: 1px solid #4A536B !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    div.stButton > button p,
    div.stButton > button span {
        color: #FFFFFF !important;
    }
    div.stButton > button:hover {
        background-color: #4A536B !important;
        border-color: #606C88 !important;
    }
    div.stButton > button[kind="primary"] {
        background-color: #FF4D4F !important;
        border: none !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }

    .futu-card {
        background-color: #282E3D;
        border: 1px solid #3A4154;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }

    .white-box-black-text {
        background-color: #FFFFFF !important;
        border: 1px solid #CCCCCC;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 10px;
        color: #000000 !important;
    }
    .white-box-black-text * {
        color: #000000 !important;
    }

    .bankruptcy-box {
        background-color: #FFFFFF !important;
        color: #FF4D4F !important;
        border: 2px solid #FF4D4F;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .bankruptcy-box * {
        color: #FF4D4F !important;
    }

    .up-color { color: #FF4D4F !important; }
    .down-color { color: #00D26A !important; }

    .badge-up {
        background-color: rgba(255, 77, 79, 0.20);
        color: #FF4D4F;
        padding: 4px 10px;
        border-radius: 5px;
        font-weight: 700;
        font-size: 14px;
    }
    .badge-down {
        background-color: rgba(0, 210, 106, 0.20);
        color: #00D26A;
        padding: 4px 10px;
        border-radius: 5px;
        font-weight: 700;
        font-size: 14px;
    }

    /* 強制白色標籤 */
    label[data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
    }
    .stSelectbox label p, .stNumberInput label p, .stSlider label p {
        color: #FFFFFF !important;
    }
    div[data-testid="stWidgetLabel"] p {
        color: #FFFFFF !important;
    }

    /* Tab 文字白色 */
    button[data-baseweb="tab"] {
        color: #FFFFFF !important;
    }
    button[data-baseweb="tab"] p {
        color: #FFFFFF !important;
    }

    /* Dataframe 保持黑字白底 */
    [data-testid="stDataFrame"] {
        background-color: #FFFFFF !important;
        border-radius: 6px;
    }
    [data-testid="stDataFrame"] * {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }

    div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border-radius: 6px;
    }
    div[data-baseweb="select"] * {
        color: #000000 !important;
    }

    .news-item {
        background-color: #282E3D;
        border-left: 3px solid #FFFFFF;
        padding: 12px 14px;
        margin-bottom: 10px;
        border-radius: 0 6px 6px 0;
        font-size: 14px;
        color: #FFFFFF !important;
        line-height: 1.45;
    }
    .news-time {
        color: #FFFFFF !important;
        font-size: 11px;
        margin-bottom: 4px;
        display: block;
        opacity: 0.8;
    }
    .ob-row {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        padding: 4px 8px;
        border-bottom: 1px solid #353B4B;
    }

    .order-confirm-box {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #CCCCCC;
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 12px;
        font-weight: 600;
    }
    .order-confirm-box * {
        color: #000000 !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. STOCK CATALOG
# -----------------------------------------------------------------------------
STOCK_CATALOG = {
    "0700.HK": {"name": "Tencent Holdings", "market": "HK", "currency": "HKD", "price": 315.20, "pe": 19.8, "mkt_cap": "3.02T", "sector": "Tech & Gaming", "lot": 100, "volatility": 0.011},
    "9988.HK": {"name": "Alibaba Group", "market": "HK", "currency": "HKD", "price": 74.50, "pe": 16.4, "mkt_cap": "1.45T", "sector": "E-Commerce & AI", "lot": 100, "volatility": 0.013},
    "01810.HK": {"name": "Xiaomi Corp.", "market": "HK", "currency": "HKD", "price": 29.85, "pe": 31.2, "mkt_cap": "745B", "sector": "Consumer Tech & EV", "lot": 200, "volatility": 0.014},
    "00005.HK": {"name": "HSBC Holdings", "market": "HK", "currency": "HKD", "price": 71.20, "pe": 8.1, "mkt_cap": "1.29T", "sector": "Banking", "lot": 400, "volatility": 0.008},
    "00388.HK": {"name": "HKEX", "market": "HK", "currency": "HKD", "price": 312.40, "pe": 30.5, "mkt_cap": "396B", "sector": "Financials", "lot": 100, "volatility": 0.010},
    "NVDA":    {"name": "NVIDIA Corporation", "market": "US", "currency": "USD", "price": 880.00, "pe": 44.2, "mkt_cap": "2.18T", "sector": "Semiconductors", "lot": 1, "volatility": 0.018},
    "MSFT":    {"name": "Microsoft Corporation", "market": "US", "currency": "USD", "price": 420.00, "pe": 35.1, "mkt_cap": "3.12T", "sector": "Cloud & AI", "lot": 1, "volatility": 0.010},
    "AAPL":    {"name": "Apple Inc.", "market": "US", "currency": "USD", "price": 182.50, "pe": 32.4, "mkt_cap": "2.81T", "sector": "Consumer Tech", "lot": 1, "volatility": 0.011},
    "TSLA":    {"name": "Tesla Inc.", "market": "US", "currency": "USD", "price": 235.00, "pe": 78.5, "mkt_cap": "750B", "sector": "EV & Robotics", "lot": 1, "volatility": 0.020},
    "GOOG":    {"name": "Alphabet Inc.", "market": "US", "currency": "USD", "price": 175.00, "pe": 26.2, "mkt_cap": "2.15T", "sector": "Search & AI", "lot": 1, "volatility": 0.012},
    "TSM":     {"name": "TSMC (ADR)", "market": "US", "currency": "USD", "price": 198.40, "pe": 29.6, "mkt_cap": "1.03T", "sector": "Semiconductors", "lot": 1, "volatility": 0.014},
    "BTC":     {"name": "Bitcoin Index", "market": "Crypto", "currency": "USD", "price": 64200.0, "pe": 0.0, "mkt_cap": "1.26T", "sector": "Digital Asset", "lot": 1, "volatility": 0.024},
}

def generate_initial_history(base_price, periods=60):
    np.random.seed(int(base_price * 10) % 10000)
    dates = [datetime.now() - timedelta(days=periods - i) for i in range(periods)]
    prices = [base_price * random.uniform(0.90, 0.97)]
    for _ in range(periods - 1):
        change = np.random.normal(0.001, 0.018)
        prices.append(max(1.0, prices[-1] * (1 + change)))
    prices[-1] = base_price

    rows = []
    for i, dt in enumerate(dates):
        close_p = prices[i]
        open_p = prices[i-1] if i > 0 else close_p * random.uniform(0.99, 1.01)
        high_p = max(open_p, close_p) * random.uniform(1.002, 1.02)
        low_p = min(open_p, close_p) * random.uniform(0.98, 0.998)
        vol = int(random.uniform(5_000_000, 35_000_000))
        pred_vol = int(vol * random.uniform(0.88, 1.15))
        rows.append({
            "Date": dt.strftime("%Y-%m-%d"),
            "Open": round(open_p, 2),
            "High": round(high_p, 2),
            "Low": round(low_p, 2),
            "Close": round(close_p, 2),
            "Volume": vol,
            "Predicted_Volume": pred_vol
        })
    return pd.DataFrame(rows)

def generate_intraday_series(current_price, prev_close):
    times = pd.date_range("09:30", "16:00", freq="5min")
    n = len(times)
    path = np.linspace(prev_close, current_price, n)
    noise = np.random.normal(0, current_price * 0.0025, n)
    noise[0] = 0
    noise[-1] = 0
    prices = np.round(path + noise, 2)
    vols = np.random.randint(100_000, 850_000, size=n)
    pred_vols = (vols * np.random.uniform(0.88, 1.15, size=n)).astype(int)
    return pd.DataFrame({
        "Time": [t.strftime("%H:%M") for t in times],
        "Price": prices,
        "Volume": vols,
        "Predicted_Volume": pred_vols
    })

# -----------------------------------------------------------------------------
# 3. NEWS
# -----------------------------------------------------------------------------
REAL_NEWS_POOL = [
    ("NVDA", "NVIDIA Board announces CEO Jensen Huang has stepped down; CFO Colette Kress appointed interim CEO.", -0.055),
    ("NVDA", "Next-generation AI data center cluster orders exceed annual wafer and packaging capacity forecasts.", 0.060),
    ("NVDA", "Export licensing reviews tightened on high-bandwidth memory and flagship compute accelerators.", -0.048),
    ("MSFT", "Enterprise cloud software spending accelerates as Fortune 500 firms migrate core workloads to Azure.", 0.042),
    ("MSFT", "Global enterprise software licensing renewal cycle slows down amid IT budget scrutiny.", -0.035),
    ("0700.HK", "Monthly mobile gaming approvals expand alongside double-digit video account advertising growth.", 0.050),
    ("0700.HK", "Major institutional shareholder discloses routine block reduction via Hong Kong clearing house.", -0.038),
    ("9988.HK", "Alibaba explores Hong Kong listing spin-off for its custom AI semiconductor design unit.", 0.046),
    ("9988.HK", "Cross-border e-commerce platforms face heightened regulatory compliance audits across key hubs.", -0.044),
    ("01810.HK", "Smart EV delivery backlog stretches past 24 weeks as second-phase Beijing factory ramps output.", 0.052),
    ("01810.HK", "Smartphone component cost inflation pressures quarterly hardware gross margin guidance.", -0.036),
    ("00388.HK", "HKEX reports record average daily ETP turnover as southbound Stock Connect inflows surge.", 0.040),
    ("00388.HK", "Secondary listing pipeline faces temporary procedural delays amid global rate volatility.", -0.030),
    ("00005.HK", "HKMA maintains steady liquidity operations as cross-boundary wealth management connect expands.", 0.028),
    ("00005.HK", "Net interest margin compression weighs on regional commercial lending revenue forecasts.", -0.026),
    ("AAPL", "Flagship smartphone pre-orders beat supply chain estimates across East Asia and Europe.", 0.042),
    ("AAPL", "European competition regulators open fresh review into App Store developer fee structures.", -0.038),
    ("TSLA", "Safety regulators open formal inquiry into full self-driving fleet telemetry logs.", -0.062),
    ("TSLA", "Lithium refining capacity expands rapidly, lowering battery pack unit manufacturing costs.", 0.050),
    ("GOOG", "Multimodal search architecture rollout drives higher commercial ad click-through conversion.", 0.044),
    ("GOOG", "Antitrust remedies proposal targets default mobile browser search distribution agreements.", -0.045),
    ("TSM", "Foundry monthly revenue climbs 4.8% YoY on sustained 3nm and 2nm node utilization.", 0.048),
    ("TSM", "Overseas fab construction schedule faces skilled labor bottlenecks and higher capex.", -0.035),
    ("BTC", "Sovereign wealth fund filings reveal fresh institutional allocations into spot digital asset ETFs.", 0.065),
    ("BTC", "Major derivatives exchange reports sudden cascade of leveraged long liquidations.", -0.058),
]

FAKE_NEWS_POOL = [
    ("NVDA", "NVIDIA announces it will stop making GPUs entirely to pivot toward artisanal sourdough bakeries.", 0.0),
    ("0700.HK", "Tencent plans to replace all WeChat text messages with mandatory 30-second interpretive dance clips.", 0.0),
    ("TSLA", "Tesla unveils a Cyber-Submarine powered exclusively by unresolved social media debates.", 0.0),
    ("MSFT", "Microsoft Windows 12 will reportedly require users to solve a Rubik's cube before opening Notepad.", 0.0),
    ("AAPL", "Apple prepares to launch iRock—a $999 anodized titanium paperweight with zero ports or buttons.", 0.0),
    ("9988.HK", "Alibaba Taobao tests quantum teleportation shipping where parcels arrive five minutes before ordering.", 0.0),
    ("01810.HK", "Xiaomi patents a smart rice cooker capable of training 70B-parameter language models while steaming.", 0.0),
    ("00005.HK", "HSBC applies for a banking license to open the first zero-gravity mortgage branch on the Moon.", 0.0),
    ("GOOG", "Alphabet announces Google Search will return answers exclusively in medieval haiku format next month.", 0.0),
    ("BTC", "Anonymous miners claim to have discovered the final Bitcoin hidden inside a vintage floppy disk.", 0.0),
    ("TSM", "TSMC engineers announce breakthrough 0.001nm chips carved using microscopic origami techniques.", 0.0),
    ("00388.HK", "HKEX proposes replacing the closing auction bell with a live karaoke performance by listed CEOs.", 0.0),
]

def get_next_fair_news():
    if not st.session_state.news_queue:
        tickers = list(STOCK_CATALOG.keys())
        random.shuffle(tickers)
        st.session_state.news_queue = tickers

    ticker = st.session_state.news_queue.pop(0)
    timestamp = datetime.now().strftime("%H:%M:%S")

    is_real = random.random() < 0.75
    if is_real:
        matching = [n for n in REAL_NEWS_POOL if n[0] == ticker]
        _, headline, base_impact = random.choice(matching if matching else REAL_NEWS_POOL)
        actual_impact = base_impact * random.uniform(0.85, 1.25)
    else:
        matching = [n for n in FAKE_NEWS_POOL if n[0] == ticker]
        _, headline, _ = random.choice(matching if matching else FAKE_NEWS_POOL)
        actual_impact = 0.0

    return {
        "time": timestamp,
        "ticker": ticker,
        "headline": headline,
        "impact": actual_impact,
        "is_real": is_real
    }

# -----------------------------------------------------------------------------
# 4. SESSION STATE
# -----------------------------------------------------------------------------
FIXED_YT_URL = "https://youtu.be/ZRtdQ81jPUQ?si=4dcyfGLSfF2Fa-J3"
MAX_LOAN = 1000000.0

def reset_simulation():
    st.session_state.cash = 100000.0
    st.session_state.bank_loan = 0.0
    st.session_state.bankrupt = False
    st.session_state.confirm_bankruptcy = False
    st.session_state.selected_ticker = "NVDA"
    st.session_state.tick_count = 0.0
    st.session_state.news_queue = []
    st.session_state.next_news_in = random.randint(15, 18)
    st.session_state.stocks = {}
    st.session_state.history = {}
    st.session_state.intraday = {}
    st.session_state.portfolio = {sym: 0.0 for sym in STOCK_CATALOG}
    st.session_state.margin_debt = {sym: 0.0 for sym in STOCK_CATALOG}
    st.session_state.trade_history = []
    st.session_state.last_order_msg = ""

    for sym, info in STOCK_CATALOG.items():
        prev_close = round(info["price"] * random.uniform(0.988, 1.012), 2)
        df_hist = generate_initial_history(info["price"])
        st.session_state.stocks[sym] = {
            **info,
            "prev_close": prev_close,
            "open": round(prev_close * random.uniform(0.996, 1.004), 2),
            "high": max(info["price"], prev_close),
            "low": min(info["price"], prev_close),
            "volume": int(df_hist.iloc[-1]["Volume"]),
            "pred_volume": int(df_hist.iloc[-1]["Predicted_Volume"]),
        }
        st.session_state.history[sym] = df_hist
        st.session_state.intraday[sym] = generate_intraday_series(info["price"], prev_close)

    st.session_state.news_feed = [get_next_fair_news()]

if "stocks" not in st.session_state:
    reset_simulation()

def advance_market(dt_sec=15.0):
    st.session_state.tick_count += dt_sec
    if st.session_state.bank_loan > 0:
        st.session_state.bank_loan += st.session_state.bank_loan * 0.00003 * dt_sec

    st.session_state.next_news_in -= dt_sec
    active_news = None
    if st.session_state.next_news_in <= 0:
        st.session_state.next_news_in = random.randint(15, 18)
        active_news = get_next_fair_news()
        st.session_state.news_feed.insert(0, active_news)
        if len(st.session_state.news_feed) > 100:
            st.session_state.news_feed = st.session_state.news_feed[:100]

    for sym, s in st.session_state.stocks.items():
        drift = 0.0001
        if active_news and active_news["is_real"] and sym == active_news["ticker"]:
            drift += active_news["impact"]

        shock = np.random.normal(drift, s["volatility"] * np.sqrt(max(dt_sec, 1)))
        new_price = max(0.5, round(s["price"] * (1 + shock), 2))
        s["price"] = new_price
        s["high"] = max(s["high"], new_price)
        s["low"] = min(s["low"], new_price)

        vol_boost = 3.0 if (active_news and active_news["is_real"] and sym == active_news["ticker"]) else 1.0
        added_vol = int(random.uniform(50_000, 300_000) * dt_sec * vol_boost)
        s["volume"] += added_vol
        s["pred_volume"] = int(s["volume"] * random.uniform(1.04, 1.25))

        intra = st.session_state.intraday[sym]
        try:
            last_time = datetime.strptime(str(intra.iloc[-1]["Time"]), "%H:%M")
            new_time = (last_time + timedelta(minutes=1)).strftime("%H:%M")
        except:
            new_time = "09:30"

        new_row = pd.DataFrame([{
            "Time": new_time,
            "Price": new_price,
            "Volume": added_vol,
            "Predicted_Volume": int(added_vol * random.uniform(0.92, 1.18))
        }])
        st.session_state.intraday[sym] = pd.concat([intra.iloc[1:], new_row], ignore_index=True)

        hist = st.session_state.history[sym]
        hist.at[hist.index[-1], "Close"] = new_price
        hist.at[hist.index[-1], "High"] = max(hist.iloc[-1]["High"], new_price)
        hist.at[hist.index[-1], "Low"] = min(hist.iloc[-1]["Low"], new_price)
        hist.at[hist.index[-1], "Volume"] = s["volume"]
        hist.at[hist.index[-1], "Predicted_Volume"] = s["pred_volume"]

        shares = st.session_state.portfolio[sym]
        debt = st.session_state.margin_debt[sym]
        if shares > 0 and debt > 0:
            if shares * new_price <= debt * 1.02:
                st.session_state.portfolio[sym] = 0.0
                st.session_state.margin_debt[sym] = 0.0
                st.session_state.trade_history.insert(0, ("LIQUIDATED", sym, round(shares, 4), new_price, "Margin Call"))

# -----------------------------------------------------------------------------
# 5. SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🐂 HinaHinaPro Terminal")
    live_market = st.toggle("🟢 Auto-Stream Market", value=True)
    refresh_sec = 15.0

    st.markdown("### 📋 Watchlist (Click to Inspect)")

    # 恢復 All / HK / US / Crypto 標籤
    market_filter = st.radio(
        "Filter by Market",
        options=["All", "HK", "US", "Crypto"],
        horizontal=True,
        label_visibility="visible"
    )

    for sym, s in st.session_state.stocks.items():
        if market_filter != "All" and s["market"] != market_filter:
            continue
        chg = s["price"] - s["prev_close"]
        chg_pct = (chg / s["prev_close"]) * 100 if s["prev_close"] else 0
        arrow = "▲" if chg >= 0 else "▼"
        is_selected = (sym == st.session_state.selected_ticker)
        label = f"{'👉 ' if is_selected else ''}{sym} | ${s['price']:,.2f} ({arrow}{abs(chg_pct):.2f}%)"
        if st.button(label, key=f"btn_{sym}", use_container_width=True):
            st.session_state.selected_ticker = sym
            st.rerun()

    st.divider()
    if st.button("⚡ Advance 1 Market Tick", use_container_width=True):
        advance_market(refresh_sec)
        st.rerun()

    st.divider()
    st.subheader("🏦 Commercial Bank Facility")
    remaining_credit = max(0.0, MAX_LOAN - st.session_state.bank_loan)
    st.write(f"**Bank Debt:** ${st.session_state.bank_loan:,.2f}")
    st.write(f"**Credit Line:** ${remaining_credit:,.2f}")

    loan_amount = st.number_input("Loan/Repay Amount ($)", min_value=0.0, max_value=MAX_LOAN, value=50000.0, step=5000.0)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Borrow", use_container_width=True):
            if st.session_state.bank_loan + loan_amount <= MAX_LOAN:
                st.session_state.bank_loan += loan_amount
                st.session_state.cash += loan_amount
                st.rerun()
            else:
                st.error("Exceeds limit")
    with c2:
        if st.button("Repay", use_container_width=True):
            repay = min(loan_amount, st.session_state.bank_loan, st.session_state.cash)
            st.session_state.cash -= repay
            st.session_state.bank_loan -= repay
            st.rerun()

    if st.button("🏳️ Apply for Bankruptcy", use_container_width=True):
        st.session_state.confirm_bankruptcy = True

    if st.session_state.get("confirm_bankruptcy", False):
        st.warning("Confirm bankruptcy?")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes", use_container_width=True):
                st.session_state.portfolio = {s: 0.0 for s in STOCK_CATALOG}
                st.session_state.margin_debt = {s: 0.0 for s in STOCK_CATALOG}
                st.session_state.cash = 0.0
                st.session_state.bankrupt = True
                st.session_state.confirm_bankruptcy = False
                st.rerun()
        with c2:
            if st.button("No", use_container_width=True):
                st.session_state.confirm_bankruptcy = False
                st.rerun()

    st.divider()
    st.subheader("🎵 Background Music")
    if st.toggle("Open Music Player"):
        st.video(FIXED_YT_URL)

    st.divider()
    if st.button("🔄 Reset Simulator", use_container_width=True):
        reset_simulation()
        st.rerun()

# -----------------------------------------------------------------------------
# 6. MAIN HEADER
# -----------------------------------------------------------------------------
gross_holdings = sum(st.session_state.portfolio[s] * st.session_state.stocks[s]["price"] for s in STOCK_CATALOG)
total_margin = sum(st.session_state.margin_debt.values())
net_worth = st.session_state.cash + gross_holdings - total_margin - st.session_state.bank_loan
net_pnl = net_worth - 100000.0

if st.session_state.get("bankrupt", False) or (st.session_state.cash <= 1 and net_worth <= 1):
    st.markdown('<div class="bankruptcy-box">🚨 YOU HAVE GONE BANKRUPT!</div>', unsafe_allow_html=True)
    if st.button("Restart Simulator", type="primary"):
        reset_simulation()
        st.rerun()
    st.stop()

st.title("HinaHinaPro — Live Institutional & Retail Trading Terminal")

m1, m2, m3, m4, m5 = st.columns(5)
m1.markdown(f'<div class="white-box-black-text"><b>💵 Liquid Cash</b><br>${st.session_state.cash:,.2f}</div>', unsafe_allow_html=True)
m2.markdown(f'<div class="white-box-black-text"><b>📊 Gross Holdings</b><br>${gross_holdings:,.2f}</div>', unsafe_allow_html=True)
m3.markdown(f'<div class="white-box-black-text"><b>🏦 Bank Loan</b><br>${st.session_state.bank_loan:,.2f}</div>', unsafe_allow_html=True)
m4.markdown(f'<div class="white-box-black-text"><b>⚡ Margin Debt</b><br>${total_margin:,.2f}</div>', unsafe_allow_html=True)
m5.markdown(f'<div class="white-box-black-text"><b>🏆 Net Worth</b><br>${net_worth:,.2f}<br>({net_pnl:+,.2f})</div>', unsafe_allow_html=True)

st.divider()

# -----------------------------------------------------------------------------
# 7. SELECTED STOCK
# -----------------------------------------------------------------------------
sel = st.session_state.selected_ticker
stock = st.session_state.stocks[sel]
chg = stock["price"] - stock["prev_close"]
chg_pct = (chg / stock["prev_close"]) * 100 if stock["prev_close"] else 0
is_up = chg >= 0
main_color = "up-color" if is_up else "down-color"
badge = "badge-up" if is_up else "badge-down"
sign = "+" if is_up else ""

st.markdown(f"""
<div class="futu-card" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
    <div>
        <span style="font-size:24px; font-weight:800; color:#FFFFFF;">{stock['name']}</span>
        <span style="font-size:16px; color:#AAA; margin-left:8px;">({sel} · {stock['market']})</span>
        <span style="background:#363C4E; color:#FFF; font-size:12px; padding:3px 8px; border-radius:4px; margin-left:8px;">{stock['sector']}</span>
    </div>
    <div style="text-align:right;">
        <span style="font-size:28px; font-weight:800;" class="{main_color}">${stock['price']:,.2f}</span>
        <span class="{badge}" style="margin-left:8px;">{sign}{chg:.2f} ({sign}{chg_pct:.2f}%)</span>
    </div>
</div>
""", unsafe_allow_html=True)

q1, q2, q3, q4 = st.columns(4)
q1.markdown(f'<div class="white-box-black-text"><b>Open / Prev</b><br>${stock["open"]:.2f} / ${stock["prev_close"]:.2f}</div>', unsafe_allow_html=True)
q2.markdown(f'<div class="white-box-black-text"><b>High / Low</b><br>${stock["high"]:.2f} / ${stock["low"]:.2f}</div>', unsafe_allow_html=True)
q3.markdown(f'<div class="white-box-black-text"><b>Volume</b><br>{stock["volume"]/1e6:.2f}M</div>', unsafe_allow_html=True)
q4.markdown(f'<div class="white-box-black-text"><b>P/E · Mkt Cap</b><br>{stock["pe"]}x · {stock["mkt_cap"]}</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. CHARTS + TRADING
# -----------------------------------------------------------------------------
col_chart, col_trade = st.columns([2.3, 1])

with col_chart:
    t1, t2, t3 = st.tabs(["Daily K-Line & MA", "Intraday Price", "Traded vs Predicted Volume"])

    df_hist = st.session_state.history[sel].copy()
    df_hist["MA5"] = df_hist["Close"].rolling(5).mean()
    df_hist["MA10"] = df_hist["Close"].rolling(10).mean()

    with t1:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, row_heights=[0.7, 0.3], vertical_spacing=0.05)
        fig.add_trace(go.Candlestick(
            x=df_hist["Date"], open=df_hist["Open"], high=df_hist["High"],
            low=df_hist["Low"], close=df_hist["Close"],
            increasing_line_color="#FF4D4F", decreasing_line_color="#00D26A",
            increasing_fillcolor="#FF4D4F", decreasing_fillcolor="#00D26A", name="K"
        ), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_hist["Date"], y=df_hist["MA5"], line=dict(color="#FFD60A", width=1.5), name="MA5"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df_hist["Date"], y=df_hist["MA10"], line=dict(color="#5AC8FA", width=1.5), name="MA10"), row=1, col=1)
        colors = ["#FF4D4F" if c >= o else "#00D26A" for c, o in zip(df_hist["Close"], df_hist["Open"])]
        fig.add_trace(go.Bar(x=df_hist["Date"], y=df_hist["Volume"], marker_color=colors, name="Vol"), row=2, col=1)
        fig.update_layout(template="plotly_dark", height=420, margin=dict(l=10,r=10,t=20,b=10),
                          xaxis_rangeslider_visible=False, paper_bgcolor="#282E3D", plot_bgcolor="#282E3D")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with t2:
        df_intra = st.session_state.intraday[sel]
        color = "#FF4D4F" if is_up else "#00D26A"
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=df_intra["Time"], y=df_intra["Price"], mode="lines",
                                  line=dict(color=color, width=2), fill="tozeroy",
                                  fillcolor="rgba(255,77,79,0.15)" if is_up else "rgba(0,210,106,0.15)"))
        fig2.add_hline(y=stock["prev_close"], line_dash="dash", line_color="#888")
        fig2.update_layout(template="plotly_dark", height=420, margin=dict(l=10,r=10,t=20,b=10),
                           paper_bgcolor="#282E3D", plot_bgcolor="#282E3D")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

    with t3:
        recent = df_hist.tail(20)
        fig3 = go.Figure()
        fig3.add_trace(go.Bar(x=recent["Date"], y=recent["Volume"], name="Actual", marker_color="#FF8533"))
        fig3.add_trace(go.Scatter(x=recent["Date"], y=recent["Predicted_Volume"], name="Predicted",
                                  mode="lines+markers", line=dict(color="#66B2FF", width=2)))
        fig3.update_layout(template="plotly_dark", height=420, margin=dict(l=10,r=10,t=20,b=10),
                           paper_bgcolor="#282E3D", plot_bgcolor="#282E3D")
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

with col_trade:
    st.markdown("#### Level-2 Order Book")
    p = stock["price"]
    step = 0.5 if p > 100 else 0.1
    rng = random.Random(int(p*100))
    html = '<div class="futu-card">'
    for i in range(3,0,-1):
        html += f'<div class="ob-row"><span>Ask {i}</span><span class="down-color">${p+i*step:.2f}</span><span>{rng.randint(20,120)*stock["lot"]}</span></div>'
    html += f'<div class="ob-row" style="background:#343B4E;font-weight:700;"><span>LAST</span><span class="{main_color}">${p:.2f}</span><span>Lot {stock["lot"]}</span></div>'
    for i in range(1,4):
        html += f'<div class="ob-row"><span>Bid {i}</span><span class="up-color">${max(0.1,p-i*step):.2f}</span><span>{rng.randint(20,120)*stock["lot"]}</span></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

    st.markdown("#### Execution Desk")
    method = st.selectbox("Trading Method", [
        "Spot Buy (Cash)", "Spot Sell (Close Long)",
        "Leveraged Multiplier (Margin Loan)", "Short Sell (Bearish)",
        "Cover Short Position", "Banker Method (Institutional Block)"
    ])

    if method == "Leveraged Multiplier (Margin Loan)":
        margin_dep = st.number_input("Cash Margin Deposit ($)", min_value=100.0, value=min(5000.0, st.session_state.cash))
        mult = st.select_slider("Leverage", options=[2,5,10,20,50,100], value=10)
        exposure = margin_dep * mult
        shares_est = exposure / stock["price"]
        st.caption(f"Exposure ${exposure:,.0f} | Shares ≈ {shares_est:.2f}")
    elif method == "Banker Method (Institutional Block)":
        block_qty = st.number_input("Block Size", min_value=100, value=500, step=100)
        disc_price = round(stock["price"] * 0.985, 2)
        st.caption(f"Price ${disc_price} | Cost ${block_qty*disc_price:,.0f}")
    else:
        qty = st.number_input("Quantity (Shares)", min_value=1.0, value=10.0, step=1.0)

    if st.button("🚀 Execute Order Now", type="primary", use_container_width=True):
        msg = ""
        success = False

        if method == "Spot Buy (Cash)":
            cost = qty * stock["price"]
            if st.session_state.cash >= cost:
                st.session_state.cash -= cost
                st.session_state.portfolio[sel] += qty
                st.session_state.trade_history.insert(0, ("SPOT BUY", sel, qty, stock["price"], "Cash"))
                msg = f"Bought {qty} shares of {sel} @ ${stock['price']:,.2f}"
                success = True
            else:
                st.error("Insufficient cash")

        elif method == "Spot Sell (Close Long)":
            if st.session_state.portfolio[sel] >= qty:
                proceeds = qty * stock["price"]
                st.session_state.cash += proceeds
                st.session_state.portfolio[sel] -= qty
                st.session_state.trade_history.insert(0, ("SPOT SELL", sel, qty, stock["price"], "Closed"))
                msg = f"Sold {qty} shares of {sel} @ ${stock['price']:,.2f}"
                success = True
            else:
                st.error("Not enough shares")

        elif method == "Leveraged Multiplier (Margin Loan)":
            if st.session_state.cash >= margin_dep:
                st.session_state.cash -= margin_dep
                st.session_state.portfolio[sel] += shares_est
                st.session_state.margin_debt[sel] += (exposure - margin_dep)
                st.session_state.trade_history.insert(0, (f"{mult}x MARGIN", sel, round(shares_est,2), stock["price"], "Margin"))
                msg = f"Opened {mult}x Long {shares_est:.2f} shares of {sel}"
                success = True
            else:
                st.error("Insufficient margin cash")

        elif method == "Short Sell (Bearish)":
            st.session_state.cash += qty * stock["price"]
            st.session_state.portfolio[sel] -= qty
            st.session_state.trade_history.insert(0, ("SHORT SELL", sel, qty, stock["price"], "Short"))
            msg = f"Shorted {qty} shares of {sel}"
            success = True

        elif method == "Cover Short Position":
            if st.session_state.portfolio[sel] < 0:
                cover = min(qty, abs(st.session_state.portfolio[sel]))
                cost = cover * stock["price"]
                if st.session_state.cash >= cost:
                    st.session_state.cash -= cost
                    st.session_state.portfolio[sel] += cover
                    st.session_state.trade_history.insert(0, ("COVER SHORT", sel, cover, stock["price"], "Covered"))
                    msg = f"Covered {cover} shares of {sel}"
                    success = True
                else:
                    st.error("Insufficient cash")
            else:
                st.error("No short position")

        elif method == "Banker Method (Institutional Block)":
            cost = block_qty * disc_price
            if st.session_state.bank_loan > 0:
                st.error("Cannot use Banker Method with active bank loan")
            elif st.session_state.cash >= cost:
                st.session_state.cash -= cost
                st.session_state.portfolio[sel] += block_qty
                st.session_state.trade_history.insert(0, ("BANKER BLOCK", sel, block_qty, disc_price, "Inst -1.5%"))
                msg = f"Banker Block: {block_qty} shares of {sel} @ ${disc_price}"
                success = True
            else:
                st.error("Insufficient cash")

        if success:
            st.session_state.last_order_msg = msg
            st.rerun()

    if st.session_state.get("last_order_msg"):
        st.markdown(f'<div class="order-confirm-box">✅ {st.session_state.last_order_msg}</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. BOTTOM TABS
# -----------------------------------------------------------------------------
st.divider()
tab1, tab2, tab3 = st.tabs(["Live Market Wire", "Portfolio & Margin Status", "Order Execution Log"])

with tab1:
    st.caption("News appears every 15-18 seconds. One stock per news.")
    for item in st.session_state.news_feed[:15]:
        st.markdown(f"""
        <div class="news-item">
            <span class="news-time">{item['time']} | {item['ticker']}</span>
            <div>{item['headline']}</div>
        </div>
        """, unsafe_allow_html=True)

with tab2:
    rows = []
    for sym, shares in st.session_state.portfolio.items():
        if shares != 0 or st.session_state.margin_debt[sym] > 0:
            price = st.session_state.stocks[sym]["price"]
            rows.append({
                "Ticker": sym,
                "Name": st.session_state.stocks[sym]["name"],
                "Position": "LONG" if shares > 0 else "SHORT",
                "Shares": round(shares, 4),
                "Price": f"${price:,.2f}",
                "Value": f"${shares*price:,.2f}",
                "Margin Debt": f"${st.session_state.margin_debt[sym]:,.2f}"
            })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No active positions")

with tab3:
    if st.session_state.trade_history:
        df_log = pd.DataFrame(st.session_state.trade_history, columns=["Method", "Ticker", "Shares", "Price", "Notes"])
        st.dataframe(df_log, use_container_width=True, hide_index=True)
    else:
        st.info("No orders executed yet")

# -----------------------------------------------------------------------------
# 10. AUTO REFRESH
# -----------------------------------------------------------------------------
if live_market and not st.session_state.get("bankrupt", False):
    time.sleep(refresh_sec)
    advance_market(refresh_sec)
    st.rerun()