import streamlit as st
import pandas as pd
import numpy as np
import random

# Page configuration
st.set_page_config(
    page_title="Real-Time Stock Market Simulator",
    page_icon="📈",
    layout="wide"
)

# Initialize Session State for persistence across interactions
if "stocks" not in st.session_state:
    st.session_state.stocks = {
        "AAPL": {"name": "Apple Inc.", "price": 180.0, "history": [180.0], "volatility": 0.02},
        "TSLA": {"name": "Tesla Motors", "price": 240.0, "history": [240.0], "volatility": 0.05},
        "GOOG": {"name": "Alphabet Inc.", "price": 140.0, "history": [140.0], "volatility": 0.015},
        "BTC":  {"name": "Crypto Index", "price": 45000.0, "history": [45000.0], "volatility": 0.08},
    }

if "cash" not in st.session_state:
    st.session_state.cash = 10000.0

if "portfolio" not in st.session_state:
    st.session_state.portfolio = {sym: 0 for sym in st.session_state.stocks}

if "news_log" not in st.session_state:
    st.session_state.news_log = [("Market opened. Ready for trading!", "System", 0)]

# Predefined breaking news events (Headline, Target Ticker, Price Impact %)
NEWS_POOL = [
    ("🚀 Tech giant announces breakthrough quantum AI chip!", "AAPL", 0.06),
    ("⚠️ Regulatory antitrust investigation launched into tech sector.", "AAPL", -0.05),
    ("⚡ Battery supply chain crisis hits manufacturing lines.", "TSLA", -0.08),
    ("📈 Record quarterly vehicle deliveries reported globally!", "TSLA", 0.07),
    ("🔍 Cloud computing revenue beats analyst expectations.", "GOOG", 0.05),
    ("🚨 Data privacy breach allegations surface.", "GOOG", -0.06),
    ("🌐 Global regulatory green light given for digital assets ETF.", "BTC", 0.12),
    ("📉 Macro liquidity crunch triggers sell-off across risk assets.", "BTC", -0.10),
]

# Sidebar Controls
st.sidebar.title("🎮 Simulation Controls")
if st.sidebar.button("⏩ Advance Market Tick", use_container_width=True):
    # 1. Random Price Fluctuations (Random Walk / Geometric Brownian Motion approximation)
    for sym, data in st.session_state.stocks.items():
        shock = np.random.normal(0, data["volatility"])
        new_price = max(1.0, data["price"] * (1 + shock))
        data["price"] = round(new_price, 2)
        data["history"].append(data["price"])
        if len(data["history"]) > 30:  # Keep last 30 ticks
            data["history"].pop(0)

    # 2. Random Breaking News Trigger (30% chance per tick)
    if random.random() < 0.4:
        headline, target, impact = random.choice(NEWS_POOL)
        # Apply news shock to target stock
        if target in st.session_state.stocks:
            old_p = st.session_state.stocks[target]["price"]
            new_p = max(1.0, old_p * (1 + impact))
            st.session_state.stocks[target]["price"] = round(new_p, 2)
            st.session_state.stocks[target]["history"][-1] = st.session_state.stocks[target]["price"]
        st.session_state.news_log.insert(0, (headline, target, impact))
        if len(st.session_state.news_log) > 5:
            st.session_state.news_log.pop()

if st.sidebar.button("🔄 Reset Portfolio & Market", use_container_width=True):
    for sym in st.session_state.stocks:
        base = 45000.0 if sym == "BTC" else (240.0 if sym == "TSLA" else (180.0 if sym == "AAPL" else 140.0))
        st.session_state.stocks[sym]["price"] = base
        st.session_state.stocks[sym]["history"] = [base]
    st.session_state.cash = 10000.0
    st.session_state.portfolio = {sym: 0 for sym in st.session_state.stocks}
    st.session_state.news_log = [("Market reset. Ready for trading!", "System", 0)]

# Main Dashboard Layout
st.title("📊 Live Stock Market & Breaking News Simulator")

# Portfolio & Cash Overview
col1, col2, col3 = st.columns(3)
portfolio_value = sum(st.session_state.portfolio[sym] * st.session_state.stocks[sym]["price"] for sym in st.session_state.stocks)
total_net_worth = st.session_state.cash + portfolio_value

col1.metric("💵 Available Cash", f"${st.session_state.cash:,.2f}")
col2.metric("📈 Portfolio Value", f"${portfolio_value:,.2f}")
col3.metric("🏆 Total Net Worth", f"${total_net_worth:,.2f}", delta=f"${total_net_worth - 10000:,.2f}")

st.divider()

# Market Quotes & Trading Section
st.subheader("📋 Market Ticker & Trading Desk")

cols = st.columns(len(st.session_state.stocks))
for i, (sym, data) in enumerate(st.session_state.stocks.items()):
    with cols[i]:
        prev_p = data["history"][-2] if len(data["history"]) > 1 else data["price"]
        change_pct = ((data["price"] - prev_p) / prev_p) * 100
        
        st.markdown(f"### **{sym}**")
        st.write(f"*{data['name']}*")
        st.metric("Price", f"${data['price']:,.2f}", delta=f"{change_pct:+.2f}%")
        
        # Mini Charting
        df_history = pd.DataFrame(data["history"], columns=["Price"])
        st.line_chart(df_history, height=120)
        
        # Trading buttons
        shares_owned = st.session_state.portfolio[sym]
        st.caption(f"Owned: {shares_owned} shares")
        
        if st.button(f"Buy {sym}", key=f"buy_{sym}"):
            if st.session_state.cash >= data["price"]:
                st.session_state.cash -= data["price"]
                st.session_state.portfolio[sym] += 1
                st.success(f"Bought 1 share of {sym}!")
                st.rerun()
            else:
                st.error("Not enough cash!")
                
        if st.button(f"Sell {sym}", key=f"sell_{sym}"):
            if shares_owned > 0:
                st.session_state.cash += data["price"]
                st.session_state.portfolio[sym] -= 1
                st.success(f"Sold 1 share of {sym}!")
                st.rerun()
            else:
                st.error("No shares to sell!")

st.divider()

# Breaking News Feed Section
st.subheader("📰 Live Breaking News Feed")
for headline, target, impact in st.session_state.news_log:
    if target == "System":
        st.info(f"**[SYSTEM]** {headline}")
    else:
        badge_color = "🟢" if impact > 0 else "🔴"
        st.markdown(f"{badge_color} **[{target} ({impact:+.0%})]** {headline}")