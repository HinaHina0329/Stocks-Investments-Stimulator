import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
from datetime import datetime, timedelta
import time

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & CSS
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
    .futu-label {
        font-size: 12px;
        color: #C5CEE0;
        margin-bottom: 4px;
        font-weight: 500;
    }
    .futu-val {
        font-size: 18px;
        font-weight: 700;
        color: #FFFFFF;
    }
    .up-color { color: #FF4D4F !important; }
    .down-color { color: #00D26A !important; }
    .flat-color { color: #C5CEE0 !important; }
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
    .news-item {
        background-color: #282E3D;
        border-left: 3px solid #788296;
        padding: 12px 14px;
        margin-bottom: 10px;
        border-radius: 0 6px 6px 0;
        font-size: 14px;
        color: #FFFFFF;
        line-height: 1.45;
    }
    .news-time {
        color: #A0ACB8;
        font-size: 11px;
        margin-bottom: 4px;
        display: block;
    }
    .ob-row {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        padding: 4px 8px;
        border-bottom: 1px solid #353B4B;
    }
    p, label, span, div, h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
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
        open_p = prices[i - 1] if i > 0 else close_p * random.uniform(0.99, 1.01)
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
# 3. NEWS POOLS
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

# -----------------------------------------------------------------------------
# 4. SESSION STATE INITIALIZATION
# -----------------------------------------------------------------------------
FIXED_YT_URL = "https://youtu.be/ZRtdQ81jPUQ?si=4dcyfGLSfF2Fa-J3"
MAX_LOAN = 1000000.0

def reset_simulation():
    st.session_state.cash = 100000.0
    st.session_state.bank_loan = 0.0
    st.session_state.bankrupt = False
    st.session_state.confirm_bankruptcy = False
    st.session_state.selected_ticker = "NVDA"
    st.session_state.simulation_time = 0.0
    st.session_state.stocks = {}
    st.session_state.history = {}
    st.session_state.intraday = {}
    st.session_state.portfolio = {sym: 0.0 for sym in STOCK_CATALOG}
    st.session_state.margin_debt = {sym: 0.0 for sym in STOCK_CATALOG}
    st.session_state.trade_history = []
    st.session_state.news_feed = []

    # 新聞控制
    st.session_state.news_queue = list(STOCK_CATALOG.keys())
    random.shuffle(st.session_state.news_queue)
    st.session_state.next_news_time = 16.0          # 第一次新聞大約 16 秒後
    st.session_state.last_advance_time = time.time()

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

if "stocks" not in st.session_state:
    reset_simulation()

# -----------------------------------------------------------------------------
# 5. MARKET ADVANCE FUNCTION
# -----------------------------------------------------------------------------
def advance_market(dt_sec=1.0):
    st.session_state.simulation_time += dt_sec
    current_t = st.session_state.simulation_time

    # 銀行利息
    if st.session_state.bank_loan > 0:
        st.session_state.bank_loan += st.session_state.bank_loan * 0.00003

    # ----- 新聞邏輯：每 15~18 秒一則，每輪每支股票最多一則 -----
    if current_t >= st.session_state.next_news_time:
        if not st.session_state.news_queue:
            st.session_state.news_queue = list(STOCK_CATALOG.keys())
            random.shuffle(st.session_state.news_queue)

        sym = st.session_state.news_queue.pop(0)
        is_real = random.random() < 0.75

        if is_real:
            matching = [n for n in REAL_NEWS_POOL if n[0] == sym]
            _, headline, impact = random.choice(matching if matching else REAL_NEWS_POOL)
            actual_impact = impact * random.uniform(0.85, 1.25)
        else:
            matching = [n for n in FAKE_NEWS_POOL if n[0] == sym]
            _, headline, _ = random.choice(matching if matching else FAKE_NEWS_POOL)
            actual_impact = 0.0

        news_item = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "ticker": sym,
            "headline": headline,
            "impact": actual_impact,
            "is_real": is_real
        }
        st.session_state.news_feed.insert(0, news_item)
        if len(st.session_state.news_feed) > 80:
            st.session_state.news_feed = st.session_state.news_feed[:80]

        # 下一次新聞時間（15~18秒後）
        st.session_state.next_news_time = current_t + random.uniform(15.0, 18.0)

        # 只有真實新聞才影響股價
        if is_real and actual_impact != 0.0:
            s = st.session_state.stocks[sym]
            s["price"] = max(0.5, round(s["price"] * (1 + actual_impact), 2))
            s["high"] = max(s["high"], s["price"])
            s["low"] = min(s["low"], s["price"])

    # ----- 所有股票自然波動（保留）-----
    for sym, s in st.session_state.stocks.items():
        shock = np.random.normal(0.00012, s["volatility"])
        new_price = max(0.5, round(s["price"] * (1 + shock), 2))
        s["price"] = new_price
        s["high"] = max(s["high"], new_price)
        s["low"] = min(s["low"], new_price)

        added_vol = int(random.uniform(100_000, 800_000))
        s["volume"] += added_vol
        s["pred_volume"] = int(s["volume"] * random.uniform(1.03, 1.20))

        # 更新 intraday
        intra = st.session_state.intraday[sym]
        try:
            last_t = datetime.strptime(str(intra.iloc[-1]["Time"]), "%H:%M")
            new_time = (last_t + timedelta(minutes=1)).strftime("%H:%M")
        except:
            new_time = "09:30"

        new_row = pd.DataFrame([{
            "Time": new_time,
            "Price": new_price,
            "Volume": added_vol,
            "Predicted_Volume": int(added_vol * random.uniform(0.9, 1.15))
        }])
        st.session_state.intraday[sym] = pd.concat([intra.iloc[1:], new_row], ignore_index=True)

        # 更新日K
        hist = st.session_state.history[sym]
        hist.at[hist.index[-1], "Close"] = new_price
        hist.at[hist.index[-1], "High"] = max(hist.iloc[-1]["High"], new_price)
        hist.at[hist.index[-1], "Low"] = min(hist.iloc[-1]["Low"], new_price)
        hist.at[hist.index[-1], "Volume"] = s["volume"]
        hist.at[hist.index[-1], "Predicted_Volume"] = s["pred_volume"]

        # 保證金強平檢查
        shares = st.session_state.portfolio[sym]
        debt = st.session_state.margin_debt[sym]
        if shares > 0 and debt > 0:
            if shares * new_price <= debt * 1.02:
                st.session_state.portfolio[sym] = 0.0
                st.session_state.margin_debt[sym] = 0.0
                st.session_state.trade_history.insert(0, ("LIQUIDATED", sym, round(shares, 4), new_price, "Margin Call"))

# -----------------------------------------------------------------------------
# 6. SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🐂 HinaHinaPro Terminal")
    live_market = st.toggle("🟢 Auto-Stream Market", value=True, key="live_market_toggle")
    refresh_sec = st.slider("Refresh Speed (Seconds)", min_value=0.8, max_value=3.0, value=1.5, step=0.1)

    st.markdown("### 📋 Watchlist")
    market_filter = st.radio("Market Filter", ["All", "HK", "US", "Crypto"], horizontal=True, label_visibility="collapsed")
    
    for sym, s in st.session_state.stocks.items():
        if market_filter != "All" and s["market"] != market_filter:
            continue
        chg = s["price"] - s["prev_close"]
        chg_pct = (chg / s["prev_close"]) * 100 if s["prev_close"] else 0
        arrow = "▲" if chg >= 0 else "▼"
        is_selected = (sym == st.session_state.selected_ticker)
        btn_label = f"{'👉 ' if is_selected else ''}{sym} | ${s['price']:,.2f} ({arrow}{abs(chg_pct):.2f}%)"
        if st.button(btn_label, key=f"watch_{sym}", use_container_width=True):
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
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("Borrow", use_container_width=True):
            if st.session_state.bank_loan + loan_amount > MAX_LOAN:
                st.error("Exceeds credit limit!")
            else:
                st.session_state.bank_loan += loan_amount
                st.session_state.cash += loan_amount
                st.success(f"Borrowed ${loan_amount:,.2f}")
                st.rerun()
    with col_b2:
        if st.button("Repay", use_container_width=True):
            repay_amt = min(loan_amount, st.session_state.bank_loan)
            if st.session_state.cash >= repay_amt:
                st.session_state.cash -= repay_amt
                st.session_state.bank_loan -= repay_amt
                st.success(f"Repaid ${repay_amt:,.2f}")
                st.rerun()
            else:
                st.error("Insufficient cash!")

    if st.button("🏳️ Apply for Bankruptcy", use_container_width=True):
        st.session_state.confirm_bankruptcy = True

    if st.session_state.get("confirm_bankruptcy", False):
        st.warning("⚠️ Wiping all positions and cash!")
        c_yes, c_no = st.columns(2)
        with c_yes:
            if st.button("✅ Confirm", use_container_width=True):
                st.session_state.portfolio = {sym: 0.0 for sym in STOCK_CATALOG}
                st.session_state.margin_debt = {sym: 0.0 for sym in STOCK_CATALOG}
                st.session_state.cash = 0.0
                st.session_state.bankrupt = True
                st.session_state.confirm_bankruptcy = False
                st.rerun()
        with c_no:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.confirm_bankruptcy = False
                st.rerun()

    st.divider()
    st.subheader("🎵 Background Music Player")
    music_open = st.toggle("🎧 Open Music Player", value=False)
    if music_open:
        st.video(FIXED_YT_URL)

    st.divider()
    if st.button("🔄 Reset Simulator", use_container_width=True):
        reset_simulation()
        st.rerun()

# -----------------------------------------------------------------------------
# 7. BANKRUPTCY CHECK + HEADER
# -----------------------------------------------------------------------------
gross_holdings = sum(st.session_state.portfolio[sym] * st.session_state.stocks[sym]["price"] for sym in STOCK_CATALOG)
total_margin_debt = sum(st.session_state.margin_debt.values())
net_worth = st.session_state.cash + gross_holdings - total_margin_debt - st.session_state.bank_loan
net_pnl = net_worth - 100000.0

if (st.session_state.cash <= 1.0 and net_worth <= 1.0) or st.session_state.get("bankrupt", False):
    st.session_state.bankrupt = True
    st.error("🚨 **YOU HAVE GONE BANKRUPT!** All assets liquidated.")
    if st.button("🔄 Restart Simulator", type="primary"):
        reset_simulation()
        st.rerun()
    st.stop()

st.title("HinaHinaPro — Live Institutional & Retail Trading Terminal")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("💵 Liquid Cash", f"${st.session_state.cash:,.2f}")
m2.metric("📊 Gross Holdings", f"${gross_holdings:,.2f}")
m3.metric("🏦 Bank Loan Debt", f"${st.session_state.bank_loan:,.2f}")
m4.metric("⚡ Margin Leverage Debt", f"${total_margin_debt:,.2f}")
m5.metric("🏆 True Net Worth", f"${net_worth:,.2f}", delta=f"${net_pnl:+,.2f}")

st.divider()

# -----------------------------------------------------------------------------
# 8. SELECTED STOCK HEADER
# -----------------------------------------------------------------------------
sel = st.session_state.selected_ticker
stock = st.session_state.stocks[sel]
chg = stock["price"] - stock["prev_close"]
chg_pct = (chg / stock["prev_close"]) * 100 if stock["prev_close"] else 0
is_up = chg >= 0
main_color_cls = "up-color" if is_up else "down-color"
badge_cls = "badge-up" if is_up else "badge-down"
sign = "+" if is_up else ""

st.markdown(f"""
<div class="futu-card" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
    <div>
        <span style="font-size:24px; font-weight:800;">{stock['name']}</span>
        <span style="font-size:16px; color:#C5CEE0; margin-left:8px;">({sel} · {stock['market']})</span>
        <span style="background:#363C4E; font-size:12px; padding:3px 9px; border-radius:4px; margin-left:10px;">{stock['sector']}</span>
    </div>
    <div style="text-align:right;">
        <span style="font-size:30px; font-weight:800;" class="{main_color_cls}">${stock['price']:,.2f} {stock['currency']}</span>
        <span class="{badge_cls}" style="margin-left:10px;">{sign}{chg:.2f} ({sign}{chg_pct:.2f}%)</span>
    </div>
</div>
""", unsafe_allow_html=True)

q1, q2, q3, q4, q5, q6 = st.columns(6)
with q1:
    st.markdown(f'<div class="futu-card"><div class="futu-label">Open / Prev Close</div><div class="futu-val">${stock["open"]:.2f} / ${stock["prev_close"]:.2f}</div></div>', unsafe_allow_html=True)
with q2:
    st.markdown(f'<div class="futu-card"><div class="futu-label">Day High / Low</div><div class="futu-val"><span class="up-color">${stock["high"]:.2f}</span> / <span class="down-color">${stock["low"]:.2f}</span></div></div>', unsafe_allow_html=True)
with q3:
    st.markdown(f'<div class="futu-card"><div class="futu-label">Traded Volume</div><div class="futu-val">{stock["volume"]/1e6:.2f}M</div></div>', unsafe_allow_html=True)
with q4:
    st.markdown(f'<div class="futu-card"><div class="futu-label">Predicted Volume</div><div class="futu-val" style="color:#66B2FF;">{stock["pred_volume"]/1e6:.2f}M</div></div>', unsafe_allow_html=True)
with q5:
    st.markdown(f'<div class="futu-card"><div class="futu-label">Total Turnover</div><div class="futu-val">${(stock["price"] * stock["volume"])/1e6:.1f}M</div></div>', unsafe_allow_html=True)
with q6:
    st.markdown(f'<div class="futu-card"><div class="futu-label">P/E · Mkt Cap</div><div class="futu-val">{stock["pe"]}x · {stock["mkt_cap"]}</div></div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 9. CHARTS + ORDER BOOK + EXECUTION
# -----------------------------------------------------------------------------
@st.fragment
def render_main_trading_area():
    col_chart, col_trade = st.columns([2.3, 1])
    CHART_BG = "#282E3D"
    GRID_COLOR = "#363D4F"
    sel = st.session_state.selected_ticker
    stock = st.session_state.stocks[sel]
    is_up = (stock["price"] - stock["prev_close"]) >= 0
    main_color_cls = "up-color" if is_up else "down-color"

    with col_chart:
        tab1, tab2, tab3 = st.tabs(["🕯️ Daily K-Line & MA", "📈 Intraday Price", "📊 Volume"])

        df_hist = st.session_state.history[sel].copy()
        df_hist["MA5"] = df_hist["Close"].rolling(5).mean()
        df_hist["MA10"] = df_hist["Close"].rolling(10).mean()

        with tab1:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.72, 0.28])
            fig.add_trace(go.Candlestick(
                x=df_hist["Date"], open=df_hist["Open"], high=df_hist["High"],
                low=df_hist["Low"], close=df_hist["Close"],
                increasing_line_color="#FF4D4F", increasing_fillcolor="#FF4D4F",
                decreasing_line_color="#00D26A", decreasing_fillcolor="#00D26A",
                name="K-Line"
            ), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_hist["Date"], y=df_hist["MA5"], line=dict(color="#FFD60A", width=1.4), name="MA5"), row=1, col=1)
            fig.add_trace(go.Scatter(x=df_hist["Date"], y=df_hist["MA10"], line=dict(color="#5AC8FA", width=1.4), name="MA10"), row=1, col=1)
            colors = ["#FF4D4F" if c >= o else "#00D26A" for c, o in zip(df_hist["Close"], df_hist["Open"])]
            fig.add_trace(go.Bar(x=df_hist["Date"], y=df_hist["Volume"], marker_color=colors, name="Volume"), row=2, col=1)
            fig.update_layout(
                template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                font=dict(color="#FFFFFF"), height=440, margin=dict(l=10, r=10, t=20, b=10),
                xaxis_rangeslider_visible=False, uirevision=f"kline_{sel}", transition_duration=0
            )
            fig.update_xaxes(gridcolor=GRID_COLOR)
            fig.update_yaxes(gridcolor=GRID_COLOR)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

        with tab2:
            df_intra = st.session_state.intraday[sel]
            line_col = "#FF4D4F" if is_up else "#00D26A"
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df_intra["Time"], y=df_intra["Price"], mode="lines",
                line=dict(color=line_col, width=2.4), fill="tozeroy",
                fillcolor="rgba(255,77,79,0.14)" if is_up else "rgba(0,210,106,0.14)"
            ))
            fig2.add_hline(y=stock["prev_close"], line_dash="dash", line_color="#C5CEE0")
            fig2.update_layout(
                template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                font=dict(color="#FFFFFF"), height=440, margin=dict(l=10, r=10, t=20, b=10),
                uirevision=f"intra_{sel}", transition_duration=0
            )
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

        with tab3:
            recent = df_hist.tail(25)
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(x=recent["Date"], y=recent["Volume"], name="Actual", marker_color="#FF8533"))
            fig3.add_trace(go.Scatter(x=recent["Date"], y=recent["Predicted_Volume"], name="Predicted",
                                      mode="lines+markers", line=dict(color="#66B2FF", width=2.5, dash="dot")))
            fig3.update_layout(
                template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                font=dict(color="#FFFFFF"), height=440, margin=dict(l=10, r=10, t=20, b=10),
                uirevision=f"vol_{sel}", transition_duration=0
            )
            st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    with col_trade:
        st.markdown("#### 📖 Level-2 Order Book")
        p = stock["price"]
        step = 0.5 if p > 100 else 0.1
        rng = random.Random(int(p * 100))
        html = '<div class="futu-card">'
        for lvl in range(3, 0, -1):
            ask_p = p + lvl * step
            ask_q = rng.randint(15, 150) * stock["lot"]
            html += f'<div class="ob-row"><span style="color:#C5CEE0;">Ask {lvl}</span><span class="down-color">${ask_p:.2f}</span><span>{ask_q:,}</span></div>'
        html += f'<div class="ob-row" style="background:#343B4E;font-weight:700;"><span>LAST</span><span class="{main_color_cls}">${p:.2f}</span><span>Lot: {stock["lot"]}</span></div>'
        for lvl in range(1, 4):
            bid_p = max(0.1, p - lvl * step)
            bid_q = rng.randint(15, 150) * stock["lot"]
            html += f'<div class="ob-row"><span style="color:#C5CEE0;">Bid {lvl}</span><span class="up-color">${bid_p:.2f}</span><span>{bid_q:,}</span></div>'
        html += '</div>'
        st.markdown(html, unsafe_allow_html=True)

        st.markdown("#### 🎯 Execution Desk")
        method = st.selectbox("Trading Method", [
            "Spot Buy (Cash)",
            "Spot Sell (Close Long)",
            "Leveraged Multiplier (Margin Loan)",
            "Short Sell (Bearish)",
            "Cover Short Position",
            "Banker Method (Institutional Block)"
        ], key="trade_method_select")

        if method == "Leveraged Multiplier (Margin Loan)":
            margin_deposit = st.number_input("Cash Margin Deposit ($)", min_value=100.0,
                                             max_value=max(100.0, st.session_state.cash),
                                             value=min(5000.0, max(100.0, st.session_state.cash)), step=500.0)
            multiplier = st.select_slider("Leverage Multiplier", options=[2, 5, 10, 20, 50, 100], value=10)
            total_exposure = margin_deposit * multiplier
            borrowed = total_exposure - margin_deposit
            est_shares = total_exposure / stock["price"]
            st.caption(f"Exposure: ${total_exposure:,.0f} | Loan: ${borrowed:,.0f}")
        elif method == "Banker Method (Institutional Block)":
            block_shares = st.number_input("Block Size (Shares)", min_value=100, max_value=50000, value=500, step=100)
            discount_price = round(stock["price"] * 0.985, 2)
            total_cost = block_shares * discount_price
            st.caption(f"Price: ${discount_price:.2f} | Cost: ${total_cost:,.0f}")
        else:
            qty = st.number_input("Quantity (Shares)", min_value=1.0, max_value=100000.0, value=10.0, step=1.0)
            st.caption(f"Order Value: ${qty * stock['price']:,.2f}")

        if st.button("🚀 Execute Order Now", type="primary", use_container_width=True):
            if method == "Spot Buy (Cash)":
                cost = qty * stock["price"]
                if st.session_state.cash >= cost:
                    st.session_state.cash -= cost
                    st.session_state.portfolio[sel] += qty
                    st.session_state.trade_history.insert(0, ("SPOT BUY", sel, qty, stock["price"], "Cash"))
                    st.success(f"Bought {qty} {sel}")
                    st.rerun()
                else:
                    st.error("Insufficient cash!")
            elif method == "Spot Sell (Close Long)":
                if st.session_state.portfolio[sel] >= qty:
                    proceeds = qty * stock["price"]
                    if st.session_state.margin_debt[sel] > 0:
                        ratio = qty / st.session_state.portfolio[sel]
                        repay = st.session_state.margin_debt[sel] * ratio
                        st.session_state.margin_debt[sel] -= repay
                        st.session_state.cash += proceeds - repay
                    else:
                        st.session_state.cash += proceeds
                    st.session_state.portfolio[sel] -= qty
                    st.session_state.trade_history.insert(0, ("SPOT SELL", sel, qty, stock["price"], "Closed"))
                    st.success(f"Sold {qty} {sel}")
                    st.rerun()
                else:
                    st.error("Not enough shares!")
            elif method == "Leveraged Multiplier (Margin Loan)":
                if st.session_state.cash >= margin_deposit:
                    st.session_state.cash -= margin_deposit
                    st.session_state.portfolio[sel] += est_shares
                    st.session_state.margin_debt[sel] += borrowed
                    st.session_state.trade_history.insert(0, (f"{multiplier}x MARGIN", sel, round(est_shares, 4), stock["price"], f"Loan ${borrowed:,.0f}"))
                    st.success("Margin order executed")
                    st.rerun()
                else:
                    st.error("Insufficient cash for margin")
            elif method == "Short Sell (Bearish)":
                st.session_state.cash += qty * stock["price"]
                st.session_state.portfolio[sel] -= qty
                st.session_state.trade_history.insert(0, ("SHORT SELL", sel, qty, stock["price"], "Short"))
                st.warning(f"Shorted {qty} {sel}")
                st.rerun()
            elif method == "Cover Short Position":
                if st.session_state.portfolio[sel] < 0:
                    cover = min(qty, abs(st.session_state.portfolio[sel]))
                    cost = cover * stock["price"]
                    if st.session_state.cash >= cost:
                        st.session_state.cash -= cost
                        st.session_state.portfolio[sel] += cover
                        st.session_state.trade_history.insert(0, ("COVER SHORT", sel, cover, stock["price"], "Covered"))
                        st.success(f"Covered {cover}")
                        st.rerun()
                    else:
                        st.error("Insufficient cash")
                else:
                    st.error("No short position")
            elif method == "Banker Method (Institutional Block)":
                if st.session_state.bank_loan > 0:
                    st.error("Cannot use Banker Method while having bank loan")
                elif st.session_state.cash < total_cost:
                    st.error("Insufficient cash")
                else:
                    st.session_state.cash -= total_cost
                    st.session_state.portfolio[sel] += block_shares
                    st.session_state.trade_history.insert(0, ("BANKER BLOCK", sel, block_shares, discount_price, "Inst -1.5%"))
                    st.success("Block executed")
                    st.rerun()

render_main_trading_area()

# -----------------------------------------------------------------------------
# 10. BOTTOM TABS
# -----------------------------------------------------------------------------
@st.fragment
def render_bottom_tabs():
    tab1, tab2, tab3 = st.tabs(["📰 Live Market Wire", "💼 Portfolio & Margin Status", "📜 Order Execution Log"])

    with tab1:
        st.caption("News appears every 15-18 seconds. Each stock gets at most one news per round.")
        for item in st.session_state.news_feed[:20]:
            real_tag = "🟢 REAL" if item.get("is_real", False) else "🔴 FAKE"
            st.markdown(f"""
            <div class="news-item">
                <span class="news-time">{item['time']} | {item['ticker']} | {real_tag}</span>
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
                    "Gross Value": f"${shares * price:,.2f}",
                    "Margin Debt": f"${st.session_state.margin_debt[sym]:,.2f}",
                    "Net Equity": f"${shares * price - st.session_state.margin_debt[sym]:,.2f}"
                })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("No active positions")

    with tab3:
        if st.session_state.trade_history:
            st.dataframe(
                pd.DataFrame(st.session_state.trade_history, columns=["Method", "Ticker", "Shares", "Price", "Notes"]),
                use_container_width=True, hide_index=True
            )
        else:
            st.caption("No orders yet")

render_bottom_tabs()

# -----------------------------------------------------------------------------
# 11. AUTO STREAM（穩定版）
# -----------------------------------------------------------------------------
if live_market and not st.session_state.get("bankrupt", False):
    # 使用時間差控制，避免過度刷新
    now = time.time()
    last = st.session_state.get("last_advance_time", 0)
    
    if now - last >= refresh_sec:
        advance_market(refresh_sec)
        st.session_state.last_advance_time = now
        st.rerun()