import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
from datetime import datetime, timedelta

# -----------------------------------------------------------------------------
# 1. PAGE CONFIG & FUTUBULL DARK THEME CSS (RED UP / GREEN DOWN)
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
        background-color: #0B0E14;
        color: #E6EDF3;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #12161F;
        border-right: 1px solid #1F2633;
    }
    .futu-card {
        background-color: #151A24;
        border: 1px solid #222938;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }
    .futu-label {
        font-size: 12px;
        color: #8B949E;
        margin-bottom: 4px;
    }
    .futu-val {
        font-size: 18px;
        font-weight: 700;
        color: #F0F6FC;
    }
    /* Asian Market Colors: Red = Up, Green = Down */
    .up-color { color: #FF3B30 !important; }
    .down-color { color: #00C805 !important; }
    .flat-color { color: #8B949E !important; }

    .badge-up {
        background-color: rgba(255, 59, 48, 0.16);
        color: #FF3B30;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 13px;
    }
    .badge-down {
        background-color: rgba(0, 200, 5, 0.16);
        color: #00C805;
        padding: 3px 8px;
        border-radius: 4px;
        font-weight: 700;
        font-size: 13px;
    }
    .news-item {
        background-color: #151A24;
        border-left: 3px solid #FF6B00;
        padding: 10px 12px;
        margin-bottom: 8px;
        border-radius: 0 6px 6px 0;
        font-size: 13px;
    }
    .news-tag-real {
        background-color: #1F3A5F;
        color: #58A6FF;
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: 600;
        margin-right: 6px;
    }
    .news-tag-fake {
        background-color: #3D1F47;
        color: #D2A8FF;
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: 600;
        margin-right: 6px;
    }
    .ob-row {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        padding: 3px 6px;
        border-bottom: 1px solid #1C222E;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. UNIVERSE & HISTORICAL GENERATOR
# -----------------------------------------------------------------------------
STOCK_CATALOG = {
    "0700.HK": {"name": "Tencent Holdings", "market": "HK", "currency": "HKD", "price": 315.20, "pe": 19.8, "mkt_cap": "3.02T", "sector": "Tech & Gaming", "lot": 100, "volatility": 0.008},
    "9988.HK": {"name": "Alibaba Group", "market": "HK", "currency": "HKD", "price": 74.50, "pe": 16.4, "mkt_cap": "1.45T", "sector": "E-Commerce & AI", "lot": 100, "volatility": 0.010},
    "NVDA":    {"name": "NVIDIA Corporation", "market": "US", "currency": "USD", "price": 880.00, "pe": 44.2, "mkt_cap": "2.18T", "sector": "Semiconductors", "lot": 1, "volatility": 0.014},
    "MSFT":    {"name": "Microsoft Corporation", "market": "US", "currency": "USD", "price": 420.00, "pe": 35.1, "mkt_cap": "3.12T", "sector": "Cloud & AI", "lot": 1, "volatility": 0.007},
    "AAPL":    {"name": "Apple Inc.", "market": "US", "currency": "USD", "price": 182.50, "pe": 32.4, "mkt_cap": "2.81T", "sector": "Consumer Tech", "lot": 1, "volatility": 0.008},
    "TSLA":    {"name": "Tesla Inc.", "market": "US", "currency": "USD", "price": 235.00, "pe": 78.5, "mkt_cap": "750B", "sector": "EV & Robotics", "lot": 1, "volatility": 0.018},
    "GOOG":    {"name": "Alphabet Inc.", "market": "US", "currency": "USD", "price": 175.00, "pe": 26.2, "mkt_cap": "2.15T", "sector": "Search & AI", "lot": 1, "volatility": 0.009},
    "BTC":     {"name": "Bitcoin Index", "market": "Crypto", "currency": "USD", "price": 64200.0, "pe": 0.0, "mkt_cap": "1.26T", "sector": "Digital Asset", "lot": 1, "volatility": 0.020},
}

def generate_initial_history(base_price, periods=60):
    np.random.seed(int(base_price * 10) % 10000)
    dates = [datetime.now() - timedelta(days=periods - i) for i in range(periods)]
    prices = [base_price * random.uniform(0.88, 0.96)]
    for _ in range(periods - 1):
        change = np.random.normal(0.001, 0.02)
        prices.append(max(1.0, prices[-1] * (1 + change)))
    prices[-1] = base_price

    rows = []
    for i, dt in enumerate(dates):
        close_p = prices[i]
        open_p = prices[i - 1] if i > 0 else close_p * random.uniform(0.99, 1.01)
        high_p = max(open_p, close_p) * random.uniform(1.002, 1.025)
        low_p = min(open_p, close_p) * random.uniform(0.975, 0.998)
        vol = int(random.uniform(5_000_000, 35_000_000))
        pred_vol = int(vol * random.uniform(0.85, 1.18))
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
    noise = np.random.normal(0, current_price * 0.0035, n)
    noise[0] = 0
    noise[-1] = 0
    prices = np.round(path + noise, 2)
    vols = np.random.randint(100_000, 850_000, size=n)
    pred_vols = (vols * np.random.uniform(0.85, 1.20, size=n)).astype(int)
    return pd.DataFrame({
        "Time": [t.strftime("%H:%M") for t in times],
        "Price": prices,
        "Volume": vols,
        "Predicted_Volume": pred_vols
    })

# -----------------------------------------------------------------------------
# 3. INFINITE NEWS ENGINE (~75% REALITY / ~25% SATIRICAL MAKE-UP)
# -----------------------------------------------------------------------------
REAL_NEWS_POOL = [
    ("NVDA", "NVIDIA Board announces CEO Jensen Huang steps down; Colette Kress appointed interim CEO.", -0.048),
    ("NVDA", "Next-gen AI data center cluster orders exceed annual capacity forecasts.", 0.055),
    ("MSFT", "Enterprise software spending accelerates as Fortune 500 firms migrate workloads to Azure.", 0.045),
    ("0700.HK", "Mobile gaming approvals surge alongside major social ecosystem advertising revenue growth.", 0.052),
    ("9988.HK", "Alibaba explores Hong Kong listing spin-off for its custom AI semiconductor division.", 0.042),
    ("AAPL", "Flagship smartphone pre-orders beat consensus estimates across Asian and European markets.", 0.040),
    ("TSLA", "Lithium refining capacity expands rapidly, slashing battery pack production costs.", 0.035),
    ("GOOG", "New multimodal search architecture drives record digital ad click-through rates.", 0.050),
    ("BTC", "Sovereign wealth fund disclosures reveal fresh allocations into spot cryptocurrency ETFs.", 0.065),
]

MAKEUP_NEWS_POOL = [
    ("NVDA", "[SATIRE] NVIDIA announces it will stop making GPUs entirely to focus on artisanal sourdough bakeries.", -0.085),
    ("0700.HK", "[SATIRE] Tencent replaces all WeChat text messages with mandatory 30-second interpretive dance videos.", -0.052),
    ("TSLA", "[SATIRE] Tesla unveils Cyber-Submarine powered exclusively by unresolved social media arguments.", 0.041),
    ("MSFT", "[SATIRE] Microsoft Windows 12 to require users to solve Rubik's cubes before opening Notepad.", -0.033),
    ("AAPL", "[SATIRE] Apple launches iRock—a $999 anodized titanium paperweight with zero charging ports.", 0.027),
    ("9988.HK", "[SATIRE] Alibaba Taobao introduces teleportation shipping; parcels arrive 5 minutes before you order.", 0.064),
]

def generate_news_event(tick_count):
    is_real = random.random() < 0.75
    timestamp = (datetime.now() + timedelta(minutes=tick_count * 2)).strftime("%H:%M:%S")
    if is_real:
        ticker, headline, impact = random.choice(REAL_NEWS_POOL)
        source_type = "REALITY"
    else:
        ticker, headline, impact = random.choice(MAKEUP_NEWS_POOL)
        source_type = "MAKE-UP"

    actual_impact = impact * random.uniform(0.75, 1.25)
    return {
        "time": timestamp,
        "ticker": ticker,
        "headline": headline,
        "impact": actual_impact,
        "type": source_type
    }

# -----------------------------------------------------------------------------
# 4. INITIALIZE SESSION STATE
# -----------------------------------------------------------------------------
FIXED_YT_URL = "https://youtu.be/ZRtdQ81jPUQ?si=4dcyfGLSfF2Fa-J3"
MAX_LOAN = 1000000.0

def reset_simulation():
    st.session_state.cash = 100000.0
    st.session_state.bank_loan = 0.0
    st.session_state.bankrupt = False
    st.session_state.confirm_bankruptcy = False
    st.session_state.selected_ticker = "NVDA"
    st.session_state.tick_count = 0
    st.session_state.stocks = {}
    st.session_state.history = {}
    st.session_state.intraday = {}
    st.session_state.portfolio = {sym: 0.0 for sym in STOCK_CATALOG}
    st.session_state.margin_debt = {sym: 0.0 for sym in STOCK_CATALOG}
    st.session_state.trade_history = []

    for sym, info in STOCK_CATALOG.items():
        prev_close = round(info["price"] * random.uniform(0.985, 1.015), 2)
        df_hist = generate_initial_history(info["price"])
        st.session_state.stocks[sym] = {
            **info,
            "prev_close": prev_close,
            "open": round(prev_close * random.uniform(0.995, 1.005), 2),
            "high": max(info["price"], prev_close),
            "low": min(info["price"], prev_close),
            "volume": int(df_hist.iloc[-1]["Volume"]),
            "pred_volume": int(df_hist.iloc[-1]["Predicted_Volume"]),
            "high_52w": round(info["price"] * 1.28, 2),
            "low_52w": round(info["price"] * 0.65, 2),
        }
        st.session_state.history[sym] = df_hist
        st.session_state.intraday[sym] = generate_intraday_series(info["price"], prev_close)

    st.session_state.news_feed = [generate_news_event(i) for i in range(12)]
    st.session_state.news_feed.reverse()

if "stocks" not in st.session_state:
    reset_simulation()

def advance_market(n_ticks=1):
    for _ in range(n_ticks):
        st.session_state.tick_count += 1
        if st.session_state.bank_loan > 0:
            st.session_state.bank_loan += st.session_state.bank_loan * 0.00002

        news = generate_news_event(st.session_state.tick_count)
        st.session_state.news_feed.insert(0, news)
        if len(st.session_state.news_feed) > 100:
            st.session_state.news_feed.pop()

        for sym, s in st.session_state.stocks.items():
            drift = 0.00005
            if sym == news["ticker"]:
                drift += news["impact"] * 0.5
            shock = np.random.normal(drift, s["volatility"])
            new_price = max(0.5, round(s["price"] * (1 + shock), 2))
            s["price"] = new_price
            s["high"] = max(s["high"], new_price)
            s["low"] = min(s["low"], new_price)

            added_vol = int(random.uniform(120_000, 1_200_000) * (2.2 if sym == news["ticker"] else 1.0))
            s["volume"] += added_vol
            s["pred_volume"] = int(s["volume"] * random.uniform(1.05, 1.30))

            # Update Intraday
            intra = st.session_state.intraday[sym]
            new_time = (datetime.strptime(intra.iloc[-1]["Time"], "%H:%M") + timedelta(minutes=1)).strftime("%H:%M")
            new_row = pd.DataFrame([{
                "Time": new_time,
                "Price": new_price,
                "Volume": added_vol,
                "Predicted_Volume": int(added_vol * random.uniform(0.9, 1.25))
            }])
            st.session_state.intraday[sym] = pd.concat([intra.iloc[1:], new_row], ignore_index=True)

            # Update History
            hist = st.session_state.history[sym]
            hist.at[hist.index[-1], "Close"] = new_price
            hist.at[hist.index[-1], "High"] = max(hist.iloc[-1]["High"], new_price)
            hist.at[hist.index[-1], "Low"] = min(hist.iloc[-1]["Low"], new_price)
            hist.at[hist.index[-1], "Volume"] = s["volume"]
            hist.at[hist.index[-1], "Predicted_Volume"] = s["pred_volume"]

            # Margin Call check
            shares = st.session_state.portfolio[sym]
            debt = st.session_state.margin_debt[sym]
            if shares > 0 and debt > 0:
                pos_val = shares * new_price
                if pos_val <= debt * 1.02:
                    st.session_state.portfolio[sym] = 0.0
                    st.session_state.margin_debt[sym] = 0.0
                    st.session_state.trade_history.insert(0, ("LIQUIDATED", sym, round(shares, 4), new_price, "Margin Call"))
                    st.session_state.news_feed.insert(0, {
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "ticker": sym,
                        "headline": f"⚠️ MARGIN CALL: Leveraged position in {sym} forcibly liquidated.",
                        "impact": -0.05,
                        "type": "REALITY"
                    })

# -----------------------------------------------------------------------------
# 5. SIDEBAR: WATCHLIST, BANK FACILITY & MUSIC PLAYER
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🐂 HinaHinaPro Terminal")
    live_market = st.toggle("🟢 Live Market Stream (3 Ticks/Sec)", value=True)

    if st.button("⚡ Next Tick", use_container_width=True):
        advance_market(1)
        st.rerun()

    st.divider()

    # Commercial Bank Facility
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

    # Bankruptcy application
    if st.button("🏳️ Apply for Bankruptcy", use_container_width=True):
        st.session_state.confirm_bankruptcy = True

    if st.session_state.confirm_bankruptcy:
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

    st.markdown("### 📋 Watchlist (Click to Inspect)")
    market_filter = st.radio("Market Filter", ["All", "HK", "US", "Crypto"], horizontal=True, label_visibility="collapsed")
    for sym, s in st.session_state.stocks.items():
        if market_filter != "All" and s["market"] != market_filter:
            continue
        chg = s["price"] - s["prev_close"]
        chg_pct = (chg / s["prev_close"]) * 100
        arrow = "▲" if chg >= 0 else "▼"
        is_selected = (sym == st.session_state.selected_ticker)
        btn_label = f"{'👉 ' if is_selected else ''}{sym} | ${s['price']:,.2f} ({arrow}{abs(chg_pct):.2f}%)"
        if st.button(btn_label, key=f"watch_{sym}", use_container_width=True):
            st.session_state.selected_ticker = sym
            st.rerun()

# -----------------------------------------------------------------------------
# 6. BANKRUPTCY CHECK & MAIN HEADER
# -----------------------------------------------------------------------------
gross_holdings = sum(st.session_state.portfolio[sym] * st.session_state.stocks[sym]["price"] for sym in STOCK_CATALOG)
total_margin_debt = sum(st.session_state.margin_debt.values())
net_worth = st.session_state.cash + gross_holdings - total_margin_debt - st.session_state.bank_loan
net_pnl = net_worth - 100000.0

if (st.session_state.cash <= 1.0 and net_worth <= 1.0 and remaining_credit <= 1.0) or st.session_state.bankrupt:
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
# 7. SELECTED STOCK HEADER & FUNDAMENTALS
# -----------------------------------------------------------------------------
sel = st.session_state.selected_ticker
stock = st.session_state.stocks[sel]
chg = stock["price"] - stock["prev_close"]
chg_pct = (chg / stock["prev_close"]) * 100
is_up = chg >= 0
main_color_cls = "up-color" if is_up else "down-color"
badge_cls = "badge-up" if is_up else "badge-down"
sign = "+" if is_up else ""

total_turnover = stock["price"] * stock["volume"]

st.markdown(f"""
<div class="futu-card" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
    <div>
        <span style="font-size:24px; font-weight:800;">{stock['name']}</span>
        <span style="font-size:16px; color:#8B949E; margin-left:8px;">({sel} · {stock['market']})</span>
        <span style="background:#212836; color:#A3B3CC; font-size:11px; padding:3px 8px; border-radius:4px; margin-left:10px;">
            {stock['sector']}
        </span>
    </div>
    <div style="text-align:right;">
        <span style="font-size:30px; font-weight:800;" class="{main_color_cls}">
            ${stock['price']:,.2f} {stock['currency']}
        </span>
        <span class="{badge_cls}" style="margin-left:10px;">
            {sign}{chg:.2f} ({sign}{chg_pct:.2f}%)
        </span>
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
    st.markdown(f'<div class="futu-card"><div class="futu-label">Predicted Volume</div><div class="futu-val" style="color:#58A6FF;">{stock["pred_volume"]/1e6:.2f}M</div></div>', unsafe_allow_html=True)
with q5:
    st.markdown(f'<div class="futu-card"><div class="futu-label">Total Turnover</div><div class="futu-val">${total_turnover/1e6:.1f}M</div></div>', unsafe_allow_html=True)
with q6:
    st.markdown(f'<div class="futu-card"><div class="futu-label">P/E (TTM) · Mkt Cap</div><div class="futu-val">{stock["pe"]}x · {stock["mkt_cap"]}</div></div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. CHARTS & ORDER BOOK / EXECUTION DESK
# -----------------------------------------------------------------------------
col_chart, col_trade = st.columns([2.3, 1])

with col_chart:
    chart_tab1, chart_tab2, chart_tab3 = st.tabs([
        "🕯️ Daily K-Line & MA",
        "📈 Intraday Price vs. Time",
        "📊 Traded vs. Predicted Volume"
    ])

    df_hist = st.session_state.history[sel].copy()
    df_hist["MA5"] = df_hist["Close"].rolling(5).mean()
    df_hist["MA10"] = df_hist["Close"].rolling(10).mean()
    df_hist["MA20"] = df_hist["Close"].rolling(20).mean()

    with chart_tab1:
        fig_k = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.72, 0.28])
        fig_k.add_trace(go.Candlestick(
            x=df_hist["Date"], open=df_hist["Open"], high=df_hist["High"], low=df_hist["Low"], close=df_hist["Close"],
            increasing_line_color="#FF3B30", increasing_fillcolor="#FF3B30",
            decreasing_line_color="#00C805", decreasing_fillcolor="#00C805",
            name="K-Line"
        ), row=1, col=1)
        fig_k.add_trace(go.Scatter(x=df_hist["Date"], y=df_hist["MA5"], line=dict(color="#FFD60A", width=1.2), name="MA5"), row=1, col=1)
        fig_k.add_trace(go.Scatter(x=df_hist["Date"], y=df_hist["MA10"], line=dict(color="#5AC8FA", width=1.2), name="MA10"), row=1, col=1)
        
        vol_colors = ["#FF3B30" if c >= o else "#00C805" for c, o in zip(df_hist["Close"], df_hist["Open"])]
        fig_k.add_trace(go.Bar(x=df_hist["Date"], y=df_hist["Volume"], marker_color=vol_colors, name="Volume"), row=2, col=1)
        fig_k.update_layout(template="plotly_dark", paper_bgcolor="#151A24", plot_bgcolor="#151A24", height=440, margin=dict(l=10, r=10, t=20, b=10), xaxis_rangeslider_visible=False)
        st.plotly_chart(fig_k, use_container_width=True)

    with chart_tab2:
        df_intra = st.session_state.intraday[sel]
        line_col = "#FF3B30" if is_up else "#00C805"
        fig_intra = go.Figure()
        fig_intra.add_trace(go.Scatter(
            x=df_intra["Time"], y=df_intra["Price"], mode="lines",
            line=dict(color=line_col, width=2.2), fill="tozeroy",
            fillcolor="rgba(255,59,48,0.12)" if is_up else "rgba(0,200,5,0.12)", name="Price"
        ))
        fig_intra.add_hline(y=stock["prev_close"], line_dash="dash", line_color="#8B949E", annotation_text="Prev Close")
        fig_intra.update_layout(template="plotly_dark", paper_bgcolor="#151A24", plot_bgcolor="#151A24", height=440, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_intra, use_container_width=True)

    with chart_tab3:
        recent_df = df_hist.tail(25)
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Bar(x=recent_df["Date"], y=recent_df["Volume"], name="Actual Traded Volume", marker_color="#FF6B00"))
        fig_vol.add_trace(go.Scatter(x=recent_df["Date"], y=recent_df["Predicted_Volume"], name="AI Predicted Volume", mode="lines+markers", line=dict(color="#58A6FF", width=2.5, dash="dot")))
        fig_vol.update_layout(template="plotly_dark", paper_bgcolor="#151A24", plot_bgcolor="#151A24", height=440, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig_vol, use_container_width=True)

with col_trade:
    st.markdown("#### 📖 Level-2 Order Book")
    p = stock["price"]
    step = 0.50 if p > 100 else 0.10
    ob_html = '<div class="futu-card">'
    for lvl in range(3, 0, -1):
        ask_p = p + lvl * step
        ask_q = random.randint(15, 150) * stock["lot"]
        ob_html += f'<div class="ob-row"><span style="color:#8B949E;">Ask {lvl}</span><span class="down-color">${ask_p:.2f}</span><span>{ask_q:,}</span></div>'
    ob_html += f'<div class="ob-row" style="background:#1E2533; font-weight:700;"><span>LAST</span><span class="{main_color_cls}">${p:.2f}</span><span>Lot: {stock["lot"]}</span></div>'
    for lvl in range(1, 4):
        bid_p = max(0.1, p - lvl * step)
        bid_q = random.randint(15, 150) * stock["lot"]
        ob_html += f'<div class="ob-row"><span style="color:#8B949E;">Bid {lvl}</span><span class="up-color">${bid_p:.2f}</span><span>{bid_q:,}</span></div>'
    ob_html += '</div>'
    st.markdown(ob_html, unsafe_allow_html=True)

    st.markdown("#### 🎯 Execution Desk")
    trade_method = st.selectbox(
        "Trading Method",
        [
            "Spot Buy (Cash)",
            "Spot Sell (Close Long)",
            "Leveraged Multiplier (Margin Loan)",
            "Short Sell (Bearish)",
            "Cover Short Position",
            "Banker Method (Institutional Block)"
        ]
    )

    if trade_method == "Leveraged Multiplier (Margin Loan)":
        margin_deposit = st.number_input("Cash Margin Deposit ($)", min_value=100.0, max_value=st.session_state.cash, value=min(5000.0, st.session_state.cash), step=500.0)
        multiplier = st.select_slider("Leverage Multiplier", options=[2, 5, 10, 20, 50, 100], value=10)
        total_exposure = margin_deposit * multiplier
        borrowed_margin = total_exposure - margin_deposit
        est_shares = total_exposure / stock["price"]
        st.caption(f"Exposure: ${total_exposure:,.2f} | Loan: ${borrowed_margin:,.2f}")
    elif trade_method == "Banker Method (Institutional Block)":
        block_shares = st.number_input("Institutional Block Size (Shares)", min_value=100, max_value=50000, value=500, step=100)
        discount_price = round(stock["price"] * 0.985, 2)
        total_block_cost = block_shares * discount_price
        st.caption(f"Discount Price (-1.5%): ${discount_price:,.2f} | Cost: ${total_block_cost:,.2f}")
    else:
        qty = st.number_input("Quantity (Shares)", min_value=1.0, max_value=100000.0, value=10.0, step=1.0)
        order_val = qty * stock["price"]
        st.caption(f"Order Value: ${order_val:,.2f}")

    if st.button("🚀 Execute Order Now", type="primary", use_container_width=True):
        if trade_method == "Spot Buy (Cash)":
            cost = qty * stock["price"]
            if st.session_state.cash >= cost:
                st.session_state.cash -= cost
                st.session_state.portfolio[sel] += qty
                st.session_state.trade_history.insert(0, ("SPOT BUY", sel, qty, stock["price"], "Cash"))
                st.success(f"Bought {qty} {sel} @ ${stock['price']:,.2f}")
                st.rerun()
            else:
                st.error("Insufficient cash!")

        elif trade_method == "Spot Sell (Close Long)":
            if st.session_state.portfolio[sel] >= qty:
                proceeds = qty * stock["price"]
                if st.session_state.margin_debt[sel] > 0:
                    ratio = qty / st.session_state.portfolio[sel]
                    debt_repaid = st.session_state.margin_debt[sel] * ratio
                    st.session_state.margin_debt[sel] -= debt_repaid
                    net_proceeds = proceeds - debt_repaid
                    st.session_state.cash += net_proceeds
                else:
                    st.session_state.cash += proceeds
                st.session_state.portfolio[sel] -= qty
                st.session_state.trade_history.insert(0, ("SPOT SELL", sel, qty, stock["price"], "Closed"))
                st.success(f"Sold {qty} {sel} @ ${stock['price']:,.2f}")
                st.rerun()
            else:
                st.error("Not enough shares held!")

        elif trade_method == "Leveraged Multiplier (Margin Loan)":
            if st.session_state.cash >= margin_deposit:
                st.session_state.cash -= margin_deposit
                st.session_state.portfolio[sel] += est_shares
                st.session_state.margin_debt[sel] += borrowed_margin
                st.session_state.trade_history.insert(0, (f"{multiplier}x MARGIN", sel, round(est_shares, 4), stock["price"], f"Loan ${borrowed_margin:,.0f}"))
                st.success(f"Placed ${total_exposure:,.2f} ({multiplier}x) in {sel}!")
                st.rerun()
            else:
                st.error("Insufficient cash for margin deposit!")

        elif trade_method == "Short Sell (Bearish)":
            proceeds = qty * stock["price"]
            st.session_state.cash += proceeds
            st.session_state.portfolio[sel] -= qty
            st.session_state.trade_history.insert(0, ("SHORT SELL", sel, qty, stock["price"], "Short"))
            st.warning(f"Shorted {qty} {sel} @ ${stock['price']:,.2f}")
            st.rerun()

        elif trade_method == "Cover Short Position":
            if st.session_state.portfolio[sel] < 0:
                cover_qty = min(qty, abs(st.session_state.portfolio[sel]))
                cost = cover_qty * stock["price"]
                if st.session_state.cash >= cost:
                    st.session_state.cash -= cost
                    st.session_state.portfolio[sel] += cover_qty
                    st.session_state.trade_history.insert(0, ("COVER SHORT", sel, cover_qty, stock["price"], "Covered"))
                    st.success(f"Covered {cover_qty} short shares of {sel}")
                    st.rerun()
                else:
                    st.error("Insufficient cash to cover!")
            else:
                st.error("No open short position for this stock.")

        elif trade_method == "Banker Method (Institutional Block)":
            if st.session_state.bank_loan > 0:
                st.error("❌ Rejected: Banker Method prohibited while active Bank Loan exists!")
            elif st.session_state.cash < total_block_cost:
                st.error("Insufficient cash for Institutional Block!")
            else:
                st.session_state.cash -= total_block_cost
                st.session_state.portfolio[sel] += block_shares
                st.session_state.trade_history.insert(0, ("BANKER BLOCK", sel, block_shares, discount_price, "Institutional -1.5%"))
                st.success(f"Executed Banker Block for {block_shares} shares of {sel} @ ${discount_price:,.2f}!")
                st.rerun()

# -----------------------------------------------------------------------------
# 9. INFINITE NEWS FEED & PORTFOLIO/LOG TABS
# -----------------------------------------------------------------------------
st.divider()
tab_news, tab_port, tab_log = st.tabs(["📰 Infinite Market Wire", "💼 Portfolio & Margin Status", "📜 Order Execution Log"])

with tab_news:
    col_nc1, col_nc2 = st.columns([3, 1])
    with col_nc1:
        st.caption("Infinite news stream combining 75% reality events and 25% satirical developments.")
    with col_nc2:
        if st.button("🔄 Push 3 Ticks of News", use_container_width=True):
            advance_market(3)
            st.rerun()

    news_filter = st.selectbox("Filter Source", ["All News", "Reality News Only", "Make-Up / Satire Only"])
    displayed = 0
    for item in st.session_state.news_feed:
        if news_filter == "Reality News Only" and item["type"] != "REALITY":
            continue
        if news_filter == "Make-Up / Satire Only" and item["type"] != "MAKE-UP":
            continue

        tag_cls = "news-tag-real" if item["type"] == "REALITY" else "news-tag-fake"
        imp_pct = item["impact"] * 100
        imp_cls = "up-color" if imp_pct >= 0 else "down-color"
        imp_str = f"{'+' if imp_pct >= 0 else ''}{imp_pct:.1f}%"

        st.markdown(f"""
        <div class="news-item">
            <div style="margin-bottom:4px;">
                <span class="{tag_cls}">{item['type']}</span>
                <strong style="color:#FF9F0A;">[{item['ticker']}]</strong>
                <span style="color:#8B949E; font-size:11px; margin-left:6px;">{item['time']}</span>
                <span class="{imp_cls}" style="float:right; font-weight:700;">Impact: {imp_str}</span>
            </div>
            <div>{item['headline']}</div>
        </div>
        """, unsafe_allow_html=True)
        displayed += 1
        if displayed >= 12:
            break

with tab_port:
    rows = []
    for sym, shares in st.session_state.portfolio.items():
        if shares != 0 or st.session_state.margin_debt[sym] > 0:
            price = st.session_state.stocks[sym]["price"]
            gross_val = shares * price
            debt = st.session_state.margin_debt[sym]
            net_eq = gross_val - debt
            rows.append({
                "Ticker": sym,
                "Name": st.session_state.stocks[sym]["name"],
                "Position": "LONG" if shares > 0 else "SHORT",
                "Shares": round(shares, 4),
                "Market Price": f"${price:,.2f}",
                "Gross Value": f"${gross_val:,.2f}",
                "Margin Debt": f"${debt:,.2f}",
                "Net Equity": f"${net_eq:,.2f}"
            })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No active positions held.")

with tab_log:
    if st.session_state.trade_history:
        st.dataframe(pd.DataFrame(st.session_state.trade_history, columns=["Method", "Ticker", "Shares", "Exec Price", "Notes"]), use_container_width=True, hide_index=True)
    else:
        st.caption("No orders executed yet.")

# -----------------------------------------------------------------------------
# 10. REAL-TIME LOOP
# -----------------------------------------------------------------------------
if live_market and not st.session_state.bankrupt:
    import time
    time.sleep(1.0 / 3.0)
    advance_market(1)
    st.rerun()