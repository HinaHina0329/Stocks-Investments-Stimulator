import streamlit as st
import pandas as pd
import numpy as np
import random
import time

# Page configuration
st.set_page_config(
    page_title="HinaHinaPro - Live Market & Margin Terminal",
    page_icon="📈",
    layout="wide"
)

# Initialize Session State
if "stocks" not in st.session_state:
    st.session_state.stocks = {
        "0700.HK": {"name": "Tencent Holdings", "market": "HK", "price": 315.20, "history": [315.20], "volatility": 0.015},
        "9988.HK": {"name": "Alibaba Group", "market": "HK", "price": 74.50, "history": [74.50], "volatility": 0.018},
        "NVDA":    {"name": "NVIDIA Corporation", "market": "US", "price": 880.00, "history": [880.00], "volatility": 0.025},
        "MSFT":    {"name": "Microsoft Corporation", "market": "US", "price": 420.00, "history": [420.00], "volatility": 0.012},
        "AAPL":    {"name": "Apple Inc.", "market": "US", "price": 182.50, "history": [182.50], "volatility": 0.014},
        "TSLA":    {"name": "Tesla Inc.", "market": "US", "price": 235.00, "history": [235.00], "volatility": 0.030},
        "GOOG":    {"name": "Alphabet Inc.", "market": "US", "price": 175.00, "history": [175.00], "volatility": 0.015},
        "BTC":     {"name": "Bitcoin Index", "market": "Crypto", "price": 64200.0, "history": [64200.0], "volatility": 0.035},
    }

if "cash" not in st.session_state:
    st.session_state.cash = 100000.0

if "bank_loan" not in st.session_state:
    st.session_state.bank_loan = 0.0  # Max 1,000,000.0

if "portfolio" not in st.session_state:
    # Tracks net shares (positive = long, negative = short)
    st.session_state.portfolio = {sym: 0.0 for sym in st.session_state.stocks}

if "margin_debt" not in st.session_state:
    # Tracks embedded leverage debt per ticker
    st.session_state.margin_debt = {sym: 0.0 for sym in st.session_state.stocks}

if "trade_history" not in st.session_state:
    st.session_state.trade_history = []

if "news_log" not in st.session_state:
    st.session_state.news_log = [
        "🔔 HinaHinaPro Live Feed Connected. Markets are open and fluctuating in real time."
    ]

# Raw News Pool: (Headline, Hidden Target, Hidden Impact)
# Neither the target nor the impact is displayed to the user.
NEWS_POOL = [
    ("BREAKING: Central bank minutes hint at faster-than-expected monetary easing this quarter.", "Macro", 0.035),
    ("ALERT: Global shipping lanes face sudden bottleneck; freight and component costs surge.", "Macro", -0.025),
    ("TECH WIRE: Next-gen AI data center cluster orders exceed annual capacity forecasts.", "NVDA", 0.065),
    ("CLOUD REPORT: Enterprise software spending accelerates as Fortune 500 firms migrate workloads.", "MSFT", 0.045),
    ("ASIA MARKETS: Mobile gaming approvals surge alongside major social ecosystem ad growth.", "0700.HK", 0.055),
    ("REGULATORY: Cross-border e-commerce platforms face heightened antitrust scrutiny.", "9988.HK", -0.050),
    ("SUPPLY CHAIN: Flagship smartphone pre-orders beat consensus estimates across Asia and Europe.", "AAPL", 0.040),
    ("AUTO NEWS: Safety regulators open formal review into full self-driving fleet telemetry.", "TSLA", -0.075),
    ("SEARCH & AI: New multimodal search architecture drives record digital ad click-through rates.", "GOOG", 0.050),
    ("DIGITAL ASSETS: Sovereign wealth fund disclosures reveal fresh allocations into spot crypto.", "BTC", 0.070),
    ("ENERGY: Lithium refining capacity expands rapidly, slashing battery pack production costs.", "TSLA", 0.055),
    ("CHIPS: Export licensing restrictions tightened on high-bandwidth memory modules.", "NVDA", -0.060),
]

def advance_market():
    """Simulates one autonomous market tick with random walk + hidden news shocks."""
    # 1. Apply bank loan & margin interest (tiny per-tick accrual)
    if st.session_state.bank_loan > 0:
        interest = st.session_state.bank_loan * 0.0001
        st.session_state.bank_loan += interest

    # 2. Geometric Brownian Motion price fluctuations
    for sym, data in st.session_state.stocks.items():
        drift = 0.0002
        shock = np.random.normal(drift, data["volatility"])
        new_price = max(0.5, data["price"] * (1 + shock))
        data["price"] = round(new_price, 2)
        data["history"].append(data["price"])
        if len(data["history"]) > 50:
            data["history"].pop(0)

        # Check margin liquidation if leveraged position equity drops below zero
        shares = st.session_state.portfolio[sym]
        debt = st.session_state.margin_debt[sym]
        if shares > 0 and debt > 0:
            position_val = shares * data["price"]
            if position_val <= debt * 1.02:  # Maintenance margin call triggered
                st.session_state.portfolio[sym] = 0.0
                st.session_state.margin_debt[sym] = 0.0
                st.session_state.trade_history.insert(0, ("LIQUIDATED", sym, round(shares, 2), data["price"], "Margin Call"))
                st.session_state.news_log.insert(0, f"⚠️ MARGIN CALL: Leveraged position in {sym} was forcibly liquidated due to insufficient equity.")

    # 3. Unfiltered Breaking News Trigger (25% chance per tick)
    if random.random() < 0.25:
        headline, target, impact = random.choice(NEWS_POOL)
        if target == "Macro":
            for sym in st.session_state.stocks:
                noise = random.uniform(0.7, 1.3)
                p = st.session_state.stocks[sym]["price"]
                st.session_state.stocks[sym]["price"] = round(max(0.5, p * (1 + impact * noise)), 2)
                st.session_state.stocks[sym]["history"][-1] = st.session_state.stocks[sym]["price"]
        elif target in st.session_state.stocks:
            old_p = st.session_state.stocks[target]["price"]
            new_p = max(0.5, old_p * (1 + impact))
            st.session_state.stocks[target]["price"] = round(new_p, 2)
            st.session_state.stocks[target]["history"][-1] = st.session_state.stocks[target]["price"]

        # Append ONLY the raw headline — no ticker or percentage hints
        st.session_state.news_log.insert(0, f"📰 {headline}")
        if len(st.session_state.news_log) > 12:
            st.session_state.news_log.pop()

# Sidebar: Live Market Engine & Bank Credit Facility
st.sidebar.title("⚡ HinaHinaPro Engine")
live_market = st.sidebar.toggle("🟢 Live Autonomous Market", value=True)
tick_speed = st.sidebar.select_slider("Market Tick Speed (sec)", options=[1.0, 2.0, 3.0, 5.0], value=2.0)

if st.sidebar.button("⏭️ Force Single Tick", use_container_width=True):
    advance_market()
    st.rerun()

st.sidebar.divider()

# Manual Bank Loan Section (Max $1,000,000)
st.sidebar.subheader("🏦 Commercial Bank Facility")
max_loan = 1000000.0
remaining_credit = max(0.0, max_loan - st.session_state.bank_loan)
st.sidebar.write(f"**Current Bank Debt:** ${st.session_state.bank_loan:,.2f}")
st.sidebar.write(f"**Available Credit:** ${remaining_credit:,.2f}")

loan_amount = st.sidebar.number_input(
    "Enter Loan / Repayment Amount ($)",
    min_value=0.0,
    max_value=max_loan,
    value=50000.0,
    step=5000.0
)

col_b1, col_b2 = st.sidebar.columns(2)
with col_b1:
    if st.button("Borrow", use_container_width=True):
        if loan_amount <= 0:
            st.sidebar.error("Enter an amount > 0.")
        elif st.session_state.bank_loan + loan_amount > max_loan:
            st.sidebar.error("Exceeds $1,000,000 bank credit limit!")
        else:
            st.session_state.bank_loan += loan_amount
            st.session_state.cash += loan_amount
            st.sidebar.success(f"Borrowed ${loan_amount:,.2f}")
            st.rerun()

with col_b2:
    if st.button("Repay", use_container_width=True):
        if loan_amount <= 0:
            st.sidebar.error("Enter an amount > 0.")
        elif st.session_state.bank_loan == 0:
            st.sidebar.info("No active bank loan.")
        else:
            repay_actual = min(loan_amount, st.session_state.bank_loan)
            if st.session_state.cash >= repay_actual:
                st.session_state.cash -= repay_actual
                st.session_state.bank_loan -= repay_actual
                st.sidebar.success(f"Repaid ${repay_actual:,.2f}")
                st.rerun()
            else:
                st.sidebar.error("Insufficient cash to repay!")

st.sidebar.divider()
if st.sidebar.button("🔄 Reset HinaHinaPro Account", use_container_width=True):
    base_prices = {
        "0700.HK": 315.20, "9988.HK": 74.50, "NVDA": 880.00,
        "MSFT": 420.00, "AAPL": 182.50, "TSLA": 235.00,
        "GOOG": 175.00, "BTC": 64200.0
    }
    for sym in st.session_state.stocks:
        st.session_state.stocks[sym]["price"] = base_prices[sym]
        st.session_state.stocks[sym]["history"] = [base_prices[sym]]
    st.session_state.cash = 100000.0
    st.session_state.bank_loan = 0.0
    st.session_state.portfolio = {sym: 0.0 for sym in st.session_state.stocks}
    st.session_state.margin_debt = {sym: 0.0 for sym in st.session_state.stocks}
    st.session_state.trade_history = []
    st.session_state.news_log = ["🔔 HinaHinaPro Account Reset. Markets live."]
    st.rerun()

# Header & Account Metrics
st.title("🐂 HinaHinaPro — Live Institutional & Retail Trading Terminal")

gross_asset_value = sum(
    st.session_state.portfolio[sym] * st.session_state.stocks[sym]["price"]
    for sym in st.session_state.stocks
)
total_margin_debt = sum(st.session_state.margin_debt.values())
net_worth = st.session_state.cash + gross_asset_value - total_margin_debt - st.session_state.bank_loan
net_pnl = net_worth - 100000.0

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("💵 Liquid Cash", f"${st.session_state.cash:,.2f}")
m2.metric("📊 Gross Holdings", f"${gross_asset_value:,.2f}")
m3.metric("🏦 Bank Loan Debt", f"${st.session_state.bank_loan:,.2f}")
m4.metric("⚡ Margin Leverage Debt", f"${total_margin_debt:,.2f}")
m5.metric("🏆 True Net Worth", f"${net_worth:,.2f}", delta=f"${net_pnl:+,.2f}")

st.divider()

# Live Market Grid
st.subheader("📡 Live Market Watchlist")
symbols = list(st.session_state.stocks.items())
for i in range(0, len(symbols), 4):
    cols = st.columns(4)
    for j in range(4):
        if i + j < len(symbols):
            sym, data = symbols[i + j]
            with cols[j]:
                prev_p = data["history"][-2] if len(data["history"]) > 1 else data["price"]
                chg_pct = ((data["price"] - prev_p) / prev_p) * 100
                st.markdown(f"#### **{sym}** · {data['market']}")
                st.caption(data["name"])
                st.metric("Last Price", f"${data['price']:,.2f}", delta=f"{chg_pct:+.2f}%")
                st.line_chart(pd.DataFrame(data["history"], columns=["Price"]), height=85)

st.divider()

# Multi-Method Order Execution Desk
st.subheader("🎯 HinaHinaPro Multi-Method Execution Desk")
oc1, oc2, oc3 = st.columns([1.2, 1.3, 1.5])

with oc1:
    selected_sym = st.selectbox("Select Ticker", list(st.session_state.stocks.keys()))
    curr_price = st.session_state.stocks[selected_sym]["price"]
    st.info(f"**{selected_sym}** Live Quote: **${curr_price:,.2f}**")

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

with oc2:
    if trade_method == "Leveraged Multiplier (Margin Loan)":
        margin_deposit = st.number_input("Your Cash Margin Deposit ($)", min_value=100.0, max_value=1000000.0, value=5000.0, step=500.0)
        multiplier = st.select_slider("Leverage Multiplier", options=[2, 5, 10, 20, 50, 100], value=100)
        total_exposure = margin_deposit * multiplier
        borrowed_margin = total_exposure - margin_deposit
        est_shares = total_exposure / curr_price
        st.write(f"**Total Position Exposure:** ${total_exposure:,.2f}")
        st.write(f"**Auto-Margin Loan:** ${borrowed_margin:,.2f}")
        st.write(f"**Shares Controlled:** {est_shares:,.4f}")
    elif trade_method == "Banker Method (Institutional Block)":
        block_shares = st.number_input("Institutional Block Size (Shares)", min_value=100, max_value=50000, value=500, step=100)
        discount_price = round(curr_price * 0.985, 2)  # 1.5% institutional block discount
        total_block_cost = block_shares * discount_price
        st.write(f"**Institutional Discount Price (-1.5%):** ${discount_price:,.2f}")
        st.write(f"**Total Block Settlement:** ${total_block_cost:,.2f}")
        if st.session_state.bank_loan > 0:
            st.error("🚫 Active Bank Loan Detected! Banker Method requires $0 bank debt.")
        else:
            st.success("✅ Debt-Free Credit Check Passed")
    else:
        qty = st.number_input("Quantity (Shares / Units)", min_value=1.0, max_value=100000.0, value=10.0, step=1.0)
        order_val = qty * curr_price
        st.write(f"**Order Value:** ${order_val:,.2f}")

with oc3:
    st.markdown("### Execution Ticket")
    st.write(f"**Available Cash:** ${st.session_state.cash:,.2f}")
    st.write(f"**Current Position ({selected_sym}):** {st.session_state.portfolio[selected_sym]:,.4f} shares")

    if st.button("🚀 Execute Order Now", use_container_width=True):
        if trade_method == "Spot Buy (Cash)":
            cost = qty * curr_price
            if st.session_state.cash >= cost:
                st.session_state.cash -= cost
                st.session_state.portfolio[selected_sym] += qty
                st.session_state.trade_history.insert(0, ("SPOT BUY", selected_sym, qty, curr_price, "Cash"))
                st.success(f"Bought {qty} {selected_sym} @ ${curr_price:,.2f}")
                st.rerun()
            else:
                st.error("Insufficient cash balance.")

        elif trade_method == "Spot Sell (Close Long)":
            if st.session_state.portfolio[selected_sym] >= qty:
                proceeds = qty * curr_price
                # Proportionally pay off any margin debt attached to this ticker
                if st.session_state.margin_debt[selected_sym] > 0:
                    ratio = qty / st.session_state.portfolio[selected_sym]
                    debt_repaid = st.session_state.margin_debt[selected_sym] * ratio
                    st.session_state.margin_debt[selected_sym] -= debt_repaid
                    net_proceeds = proceeds - debt_repaid
                    st.session_state.cash += net_proceeds
                else:
                    st.session_state.cash += proceeds
                st.session_state.portfolio[selected_sym] -= qty
                st.session_state.trade_history.insert(0, ("SPOT SELL", selected_sym, qty, curr_price, "Closed"))
                st.success(f"Sold {qty} {selected_sym} @ ${curr_price:,.2f}")
                st.rerun()
            else:
                st.error("Not enough shares held to sell.")

        elif trade_method == "Leveraged Multiplier (Margin Loan)":
            if st.session_state.cash >= margin_deposit:
                st.session_state.cash -= margin_deposit
                st.session_state.portfolio[selected_sym] += est_shares
                st.session_state.margin_debt[selected_sym] += borrowed_margin
                st.session_state.trade_history.insert(
                    0, (f"{multiplier}x MARGIN BUY", selected_sym, round(est_shares, 4), curr_price, f"Loan ${borrowed_margin:,.0f}")
                )
                st.success(f"Placed ${total_exposure:,.2f} ({multiplier}x) in {selected_sym} using ${margin_deposit:,.2f} cash!")
                st.rerun()
            else:
                st.error("Insufficient cash for margin deposit.")

        elif trade_method == "Short Sell (Bearish)":
            proceeds = qty * curr_price
            st.session_state.cash += proceeds
            st.session_state.portfolio[selected_sym] -= qty
            st.session_state.trade_history.insert(0, ("SHORT SELL", selected_sym, qty, curr_price, "Short"))
            st.warning(f"Shorted {qty} {selected_sym} @ ${curr_price:,.2f}")
            st.rerun()

        elif trade_method == "Cover Short Position":
            if st.session_state.portfolio[selected_sym] < 0:
                cover_qty = min(qty, abs(st.session_state.portfolio[selected_sym]))
                cost = cover_qty * curr_price
                if st.session_state.cash >= cost:
                    st.session_state.cash -= cost
                    st.session_state.portfolio[selected_sym] += cover_qty
                    st.session_state.trade_history.insert(0, ("COVER SHORT", selected_sym, cover_qty, curr_price, "Covered"))
                    st.success(f"Covered {cover_qty} short shares of {selected_sym}")
                    st.rerun()
                else:
                    st.error("Insufficient cash to buy back shares.")
            else:
                st.error("No open short position for this stock.")

        elif trade_method == "Banker Method (Institutional Block)":
            if st.session_state.bank_loan > 0:
                st.error("❌ REJECTED: Institutional Banker Method is strictly prohibited while you have an active Bank Loan! Repay your bank loan first.")
            elif st.session_state.cash < total_block_cost:
                st.error("Insufficient cash for Institutional Block settlement.")
            else:
                st.session_state.cash -= total_block_cost
                st.session_state.portfolio[selected_sym] += block_shares
                st.session_state.trade_history.insert(
                    0, ("BANKER BLOCK", selected_sym, block_shares, discount_price, "Institutional -1.5%")
                )
                st.success(f"Executed Banker Block: {block_shares} shares of {selected_sym} @ ${discount_price:,.2f}!")
                st.rerun()

st.divider()

# Bottom Tabs: Unfiltered News Wire, Portfolio, and Execution Log
tab_news, tab_port, tab_log = st.tabs(["📰 Unfiltered Market Wire", "💼 Portfolio & Margin Status", "📜 Order Execution Log"])

with tab_news:
    st.caption("Analyze the headlines carefully—market reactions happen immediately without hints.")
    for item in st.session_state.news_log:
        st.markdown(f"> {item}")

with tab_port:
    rows = []
    for sym, shares in st.session_state.portfolio.items():
        if shares != 0 or st.session_state.margin_debt[sym] > 0:
            price = st.session_state.stocks[sym]["price"]
            gross_val = shares * price
            debt = st.session_state.margin_debt[sym]
            net_equity = gross_val - debt
            rows.append({
                "Ticker": sym,
                "Name": st.session_state.stocks[sym]["name"],
                "Position": "LONG" if shares > 0 else "SHORT",
                "Shares": round(shares, 4),
                "Market Price": repr(f"${price:,.2f}").replace("'", ""),
                "Gross Value": repr(f"${gross_val:,.2f}").replace("'", ""),
                "Margin Debt": repr(f"${debt:,.2f}").replace("'", ""),
                "Net Equity": repr(f"${net_equity:,.2f}").replace("'", ""),
            })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True)
    else:
        st.info("No active positions held.")

with tab_log:
    if st.session_state.trade_history:
        st.dataframe(
            pd.DataFrame(st.session_state.trade_history, columns=["Method", "Ticker", "Shares", "Exec Price", "Notes"]),
            use_container_width=True
        )
    else:
        st.info("No orders executed yet.")

# Autonomous Real-Time Loop
if live_market:
    time.sleep(tick_speed)
    advance_market()
    st.rerun()