import streamlit as st
import pandas as pd
import numpy as np
import random

# Page configuration
st.set_page_config(
    page_title="Futubull-Style Advanced Stock Market Simulator",
    page_icon="📈",
    layout="wide"
)

# Initialize Session State for persistence across interactions
if "stocks" not in st.session_state:
    st.session_state.stocks = {
        "0700.HK": {"name": "Tencent Holdings", "market": "HK", "price": 315.20, "history": [315.20], "volatility": 0.025, "sector": "Tech"},
        "9988.HK": {"name": "Alibaba Group", "market": "HK", "price": 74.50, "history": [74.50], "volatility": 0.03, "sector": "E-Commerce"},
        "NVDA":    {"name": "NVIDIA Corporation", "market": "US", "price": 880.00, "history": [880.00], "volatility": 0.045, "sector": "Semiconductors/AI"},
        "MSFT":    {"name": "Microsoft Corporation", "market": "US", "price": 420.00, "history": [420.00], "volatility": 0.018, "sector": "Cloud/Software"},
        "AAPL":    {"name": "Apple Inc.", "market": "US", "price": 182.50, "history": [182.50], "volatility": 0.02, "sector": "Consumer Tech"},
        "TSLA":    {"name": "Tesla Inc.", "market": "US", "price": 235.00, "history": [235.00], "volatility": 0.05, "sector": "EV/Automotive"},
        "GOOG":    {"name": "Alphabet Inc. (Google)", "market": "US", "price": 175.00, "history": [175.00], "volatility": 0.022, "sector": "Digital Advertising"},
        "BTC":     {"name": "Bitcoin Index", "market": "Crypto", "price": 64200.0, "history": [64200.0], "volatility": 0.07, "sector": "Crypto"},
    }

if "cash" not in st.session_state:
    st.session_state.cash = 200000.0  # Starting capital

if "portfolio" not in st.session_state:
    st.session_state.portfolio = {sym: 0 for sym in st.session_state.stocks}

if "trade_history" not in st.session_state:
    st.session_state.trade_history = []

if "news_log" not in st.session_state:
    st.session_state.news_log = [("Market opened. Live Futubull trading feed initialized.", "System", 0)]

# Predefined breaking news events combining Real-world and Original shocks
NEWS_POOL = [
    ("🌐 US Federal Reserve unexpectedly signals interest rate cuts amid cooling inflation.", "Macro", 0.04),
    ("⚠️ Geopolitical supply chain bottlenecks impact global semiconductor shipments.", "Macro", -0.03),
    ("🚀 NVIDIA announces next-generation Blackwell Ultra chips with record enterprise orders.", "NVDA", 0.08),
    ("☁️ Microsoft reports staggering Azure cloud acceleration driven by enterprise AI adoption.", "MSFT", 0.06),
    ("tencent Tencent announces record gaming monetization and AI integration roadmap.", "0700.HK", 0.07),
    ("📉 Antitrust regulators tighten compliance review on major e-commerce platforms.", "9988.HK", -0.06),
    ("⚡ Apple unveils revolutionary AR/VR spatial headset iteration with high consumer demand.", "AAPL", 0.05),
    ("🚨 NHTSA launches regulatory inquiry into autonomous driving software features.", "TSLA", -0.09),
    ("🔍 Google unveils breakthrough quantum computing milestone outperforming competitors.", "GOOG", 0.07),
    ("🪙 Spot Bitcoin ETF sees massive institutional inflows breaking daily records.", "BTC", 0.08),
]

# Sidebar Controls (Futubull Trading Desk Style)
st.sidebar.title("🎮 Futubull Pro Terminal")
st.sidebar.markdown("---")

auto_advance = st.sidebar.checkbox("⚡ Enable Auto Simulation Ticks", value=False)
if st.sidebar.button("⏩ Advance Market Tick", use_container_width=True) or auto_advance:
    # 1. Price Fluctuations via Geometric Brownian Motion approximation
    for sym, data in st.session_state.stocks.items():
        shock = np.random.normal(0.0005, data["volatility"])
        new_price = max(0.5, data["price"] * (1 + shock))
        data["price"] = round(new_price, 2)
        data["history"].append(data["price"])
        if len(data["history"]) > 40:
            data["history"].pop(0)

    # 2. Breaking News Event Trigger (35% chance per tick)
    if random.random() < 0.35:
        headline, target, impact = random.choice(NEWS_POOL)
        if target == "Macro":
            for sym in st.session_state.stocks:
                st.session_state.stocks[sym]["price"] = round(max(0.5, st.session_state.stocks[sym]["price"] * (1 + impact)), 2)
        elif target in st.session_state.stocks:
            old_p = st.session_state.stocks[target]["price"]
            new_p = max(0.5, old_p * (1 + impact))
            st.session_state.stocks[target]["price"] = round(new_p, 2)
            st.session_state.stocks[target]["history"][-1] = st.session_state.stocks[target]["price"]
        
        st.session_state.news_log.insert(0, (headline, target, impact))
        if len(st.session_state.news_log) > 8:
            st.session_state.news_log.pop()

if st.sidebar.button("🔄 Reset Account & Portfolio", use_container_width=True):
    base_prices = {
        "0700.HK": 315.20, "9988.HK": 74.50, "NVDA": 880.00, 
        "MSFT": 420.00, "AAPL": 182.50, "TSLA": 235.00, 
        "GOOG": 175.00, "BTC": 64200.0
    }
    for sym in st.session_state.stocks:
        st.session_state.stocks[sym]["price"] = base_prices[sym]
        st.session_state.stocks[sym]["history"] = [base_prices[sym]]
    st.session_state.cash = 200000.0
    st.session_state.portfolio = {sym: 0 for sym in st.session_state.stocks}
    st.session_state.trade_history = []
    st.session_state.news_log = [("Account reset successfully.", "System", 0)]
    st.rerun()

# Main Dashboard Layout - Futubull Pro Style
st.title("🐂 Futubull Pro - Advanced Market & Trading Simulator")

# Financial Overview Metrics Bar
col1, col2, col3, col4 = st.columns(4)
portfolio_market_value = sum(st.session_state.portfolio[sym] * st.session_state.stocks[sym]["price"] for sym in st.session_state.stocks)
total_net_worth = st.session_state.cash + portfolio_market_value
total_pnl = total_net_worth - 200000.0
pnl_pct = (total_pnl / 200000.0) * 100

col1.metric("💰 Cash Balance", f"${st.session_state.cash:,.2f}")
col2.metric("📊 Portfolio Value", f"${portfolio_market_value:,.2f}")
col3.metric("🏆 Total Net Worth", f"${total_net_worth:,.2f}")
col4.metric("📈 Cumulative P&L", f"${total_pnl:+,.2f}", delta=f"{pnl_pct:+.2f}%")

st.divider()

# Market Quotes Grid & Interactive Trading Panel
st.subheader("📋 Market Watch & Order Execution Desk")

market_tabs = st.tabs(["🌐 All Markets", "🇭🇰 HK Stocks", "🇺🇸 US Tech Giants", "🪙 Cryptocurrencies"])

with market_tabs[0]:
    # Display tickers in rows of 4 columns
    symbols = list(st.session_state.stocks.items())
    for i in range(0, len(symbols), 4):
        cols = st.columns(4)
        for j in range(4):
            if i + j < len(symbols):
                sym, data = symbols[i + j]
                with cols[j]:
                    prev_p = data["history"][-2] if len(data["history"]) > 1 else data["price"]
                    change_pct = ((data["price"] - prev_p) / prev_p) * 100
                    
                    st.markdown(f"#### **{sym}**")
                    st.caption(f"{data['name']} ({data['sector']})")
                    st.metric("Price", f"${data['price']:,.2f}", delta=f"{change_pct:+.2f}%")
                    st.line_chart(pd.DataFrame(data["history"], columns=["Price"]), height=90)
                    st.text(f"Holding: {st.session_state.portfolio[sym]} shares")

st.divider()

# Advanced Order Execution Form (Simulating Futubull Order Ticket)
st.subheader("🛒 Place Order (Market / Limit Simulation)")
order_col1, order_col2, order_col3 = st.columns(3)

with order_col1:
    selected_stock = st.selectbox("Select Asset Symbol", list(st.session_state.stocks.keys()))
    current_asset_price = st.session_state.stocks[selected_stock]["price"]
    st.info(f"Current Market Price for **{selected_stock}**: **${current_asset_price:,.2f}**")

with order_col2:
    order_type = st.radio("Order Type", ["Market Buy", "Market Sell", "Short Sell", "Cover Short"])
    quantity = st.number_input("Quantity (Shares/Units)", min_value=1, max_value=10000, value=1, step=1)

with order_col3:
    total_cost = current_asset_price * quantity
    st.markdown("### Order Summary")
    st.write(f"**Estimated Total:** ${total_cost:,.2f}")
    st.write(f"**Available Cash:** ${st.session_state.cash:,.2f}")
    
    if st.button("🚀 Submit Order", use_container_width=True):
        if order_type == "Market Buy":
            if st.session_state.cash >= total_cost:
                st.session_state.cash -= total_cost
                st.session_state.portfolio[selected_stock] += quantity
                st.session_state.trade_history.insert(0, ("BUY", selected_stock, quantity, current_asset_price))
                st.success(f"Successfully bought {quantity} shares of {selected_stock} at ${current_asset_price:,.2f}!")
                st.rerun()
            else:
                st.error("Insufficient cash to complete transaction!")
                
        elif order_type == "Market Sell":
            if st.session_state.portfolio[selected_stock] >= quantity:
                st.session_state.cash += total_cost
                st.session_state.portfolio[selected_stock] -= quantity
                st.session_state.trade_history.insert(0, ("SELL", selected_stock, quantity, current_asset_price))
                st.success(f"Successfully sold {quantity} shares of {selected_stock} at ${current_asset_price:,.2f}!")
                st.rerun()
            else:
                st.error("You do not own enough shares to sell this quantity!")
                
        elif order_type == "Short Sell":
            st.session_state.cash += total_cost
            st.session_state.portfolio[selected_stock] -= quantity
            st.session_state.trade_history.insert(0, ("SHORT", selected_stock, quantity, current_asset_price))
            st.warning(f"Shorted {quantity} units of {selected_stock}. Monitor price movement!")
            st.rerun()
            
        elif order_type == "Cover Short":
            if st.session_state.cash >= total_cost:
                st.session_state.cash -= total_cost
                st.session_state.portfolio[selected_stock] += quantity
                st.session_state.trade_history.insert(0, ("COVER", selected_stock, quantity, current_asset_price))
                st.success(f"Covered short position for {quantity} units of {selected_stock}!")
                st.rerun()
            else:
                st.error("Insufficient cash to cover short position!")

st.divider()

# Portfolio Holdings & Real-Time News Stream
tab_portfolio, tab_news, tab_history = st.tabs(["💼 Portfolio Holdings", "📰 Breaking News & Macro Feed", "📜 Trade History"])

with tab_portfolio:
    portfolio_data = []
    for sym, shares in st.session_state.portfolio.items():
        price = st.session_state.stocks[sym]["price"]
        market_val = shares * price
        portfolio_data.append({
            "Ticker": sym,
            "Name": st.session_state.stocks[sym]["name"],
            "Shares Owned": shares,
            "Current Price": repr(f"${price:,.2f}").replace("'", ""),
            "Market Value": repr(f"${market_val:,.2f}").replace("'", "")
        })
    st.dataframe(pd.DataFrame(portfolio_data), use_container_width=True)

with tab_news:
    for headline, target, impact in st.session_state.news_log:
        if target == "System":
            st.info(f"**[SYSTEM]** {headline}")
        elif target == "Macro":
            st.warning(f"🌐 **[MACRO ECONOMIC EVENT ({impact:+.1%})]** {headline}")
        else:
            badge_color = "🟢" if impact > 0 else "🔴"
            st.markdown(f"{badge_color} **[{target} | Impact: {impact:+.0%}]** {headline}")

with tab_history:
    if st.session_state.trade_history:
        history_df = pd.DataFrame(st.session_state.trade_history, columns=["Action", "Ticker", "Quantity", "Execution Price"])
        st.dataframe(history_df, use_container_width=True)
    else:
        st.info("No trades executed yet in this session.")