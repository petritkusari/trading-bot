"""
Trading Bot Dashboard - Streamlit Web Interface
Run with: streamlit run trading_dashboard.py
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import time
from ib_insync import Stock, Option, MarketOrder, LimitOrder
from ib_connection import connect_ib

# Page configuration
st.set_page_config(
    page_title="Trading Bot Dashboard",
    page_icon="📈",
    layout="wide"
)

# Initialize session state
if 'ib' not in st.session_state:
    st.session_state.ib = None
    st.session_state.connection_info = None
    st.session_state.last_update = None

# Sidebar - Connection
st.sidebar.title("🔌 Connection")

if st.sidebar.button("Connect to IB Gateway/TWS"):
    try:
        with st.spinner("Connecting..."):
            st.session_state.ib, st.session_state.connection_info = connect_ib(client_id=1)
            st.session_state.last_update = datetime.now()
        st.sidebar.success(f"✅ Connected to {st.session_state.connection_info}")
    except Exception as e:
        st.sidebar.error(f"❌ Connection failed: {e}")

if st.session_state.ib and st.sidebar.button("Disconnect"):
    try:
        st.session_state.ib.disconnect()
        st.session_state.ib = None
        st.session_state.connection_info = None
        st.sidebar.info("Disconnected")
    except:
        pass

# Show connection status
if st.session_state.connection_info:
    st.sidebar.info(f"📡 {st.session_state.connection_info}")
    if st.session_state.last_update:
        st.sidebar.caption(f"Last update: {st.session_state.last_update.strftime('%H:%M:%S')}")
else:
    st.sidebar.warning("Not connected")

# Main title
st.title("📈 Trading Bot Dashboard")

# Check if connected
if not st.session_state.ib:
    st.warning("⚠️ Please connect to IB Gateway or TWS using the sidebar")
    st.stop()

ib = st.session_state.ib

# Auto-refresh
if st.sidebar.checkbox("Auto-refresh (5s)", value=False):
    time.sleep(5)
    st.rerun()

# Manual refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.session_state.last_update = datetime.now()
    st.rerun()

# === ACCOUNT SUMMARY ===
st.header("💰 Account Summary")

try:
    # Get account values
    account_values = ib.accountSummary()
    accounts = ib.managedAccounts()

    # Create metrics
    col1, col2, col3, col4 = st.columns(4)

    for value in account_values:
        if value.tag == 'NetLiquidation':
            col1.metric("Net Liquidation", f"${float(value.value):,.2f}")
        elif value.tag == 'TotalCashValue':
            col2.metric("Cash", f"${float(value.value):,.2f}")
        elif value.tag == 'BuyingPower':
            col3.metric("Buying Power", f"${float(value.value):,.2f}")
        elif value.tag == 'UnrealizedPnL':
            pnl = float(value.value)
            col4.metric("Unrealized P&L", f"${pnl:,.2f}",
                       delta=f"{pnl:,.2f}",
                       delta_color="normal" if pnl >= 0 else "inverse")

    st.caption(f"Account(s): {', '.join(accounts)}")

except Exception as e:
    st.error(f"Error fetching account summary: {e}")

st.divider()

# === CURRENT POSITIONS ===
st.header("📊 Current Positions")

try:
    positions = ib.positions()

    if positions:
        # Separate stocks and options
        stock_positions = []
        option_positions = []

        for pos in positions:
            pos_data = {
                'Symbol': pos.contract.symbol,
                'Position': pos.position,
                'Avg Cost': f"${pos.avgCost:.2f}",
            }

            if pos.contract.secType == 'STK':
                stock_positions.append(pos_data)
            elif pos.contract.secType == 'OPT':
                pos_data['Strike'] = pos.contract.strike
                pos_data['Type'] = pos.contract.right
                pos_data['Expiry'] = pos.contract.lastTradeDateOrContractMonth
                pos_data['Local Symbol'] = pos.contract.localSymbol
                option_positions.append(pos_data)

        # Display stocks
        if stock_positions:
            st.subheader("📈 Stock Positions")
            df_stocks = pd.DataFrame(stock_positions)
            st.dataframe(df_stocks, use_container_width=True, hide_index=True)

        # Display options
        if option_positions:
            st.subheader("📉 Option Positions")
            df_options = pd.DataFrame(option_positions)
            st.dataframe(df_options, use_container_width=True, hide_index=True)
    else:
        st.info("No open positions")

except Exception as e:
    st.error(f"Error fetching positions: {e}")

st.divider()

# === OPEN ORDERS ===
st.header("📋 Open Orders")

try:
    trades = ib.openTrades()

    if trades:
        orders_data = []
        for trade in trades:
            order_info = {
                'Symbol': trade.contract.symbol,
                'Action': trade.order.action,
                'Quantity': trade.order.totalQuantity,
                'Type': trade.order.orderType,
                'Status': trade.orderStatus.status,
                'Filled': trade.orderStatus.filled,
                'Remaining': trade.orderStatus.remaining
            }

            if hasattr(trade.contract, 'strike'):
                order_info['Strike'] = trade.contract.strike
                order_info['Option Type'] = trade.contract.right

            orders_data.append(order_info)

        df_orders = pd.DataFrame(orders_data)
        st.dataframe(df_orders, use_container_width=True, hide_index=True)
    else:
        st.info("No open orders")

except Exception as e:
    st.error(f"Error fetching orders: {e}")

st.divider()

# === TRADE EXECUTOR ===
st.header("⚡ Trade Executor")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📤 Place Order")

    symbol = st.text_input("Symbol", value="AAPL").upper()
    action = st.selectbox("Action", ["BUY", "SELL"])
    quantity = st.number_input("Quantity", min_value=1, value=100, step=1)
    order_type = st.selectbox("Order Type", ["MARKET", "LIMIT"])

    limit_price = None
    if order_type == "LIMIT":
        limit_price = st.number_input("Limit Price", min_value=0.01, value=100.00, step=0.01)

    if st.button("🚀 Execute Trade", type="primary"):
        try:
            with st.spinner(f"Placing {action} order for {quantity} {symbol}..."):
                # Create contract
                stock = Stock(symbol, 'SMART', 'USD')
                ib.qualifyContracts(stock)

                # Create order
                if order_type == "MARKET":
                    order = MarketOrder(action, quantity)
                else:
                    order = LimitOrder(action, quantity, limit_price)

                # Place order
                trade = ib.placeOrder(stock, order)
                time.sleep(2)

                st.success(f"✅ Order placed! Order ID: {trade.order.orderId}")
                st.info(f"Status: {trade.orderStatus.status}")

                # Refresh data
                time.sleep(1)
                st.rerun()

        except Exception as e:
            st.error(f"❌ Error placing order: {e}")

with col2:
    st.subheader("🔍 Quick Stock Info")

    if st.button("Get Stock Price"):
        try:
            with st.spinner(f"Fetching {symbol} price..."):
                stock = Stock(symbol, 'SMART', 'USD')
                ib.qualifyContracts(stock)

                ib.reqMarketDataType(3)  # Delayed data
                ticker = ib.reqMktData(stock, '', False, False)
                time.sleep(2)

                if ticker.last and ticker.last > 0:
                    price = ticker.last
                elif ticker.close and ticker.close > 0:
                    price = ticker.close
                else:
                    price = "N/A"

                if price != "N/A":
                    st.metric(f"{symbol} Price", f"${price:.2f}")
                    st.caption(f"Order value: ${price * quantity:,.2f}")
                else:
                    st.warning("Price data not available")

        except Exception as e:
            st.error(f"Error fetching price: {e}")

st.divider()

# === OPTION ANALYZER ===
st.header("🎯 Option Analyzer")

if st.button("🔍 Analyze All Options"):
    try:
        with st.spinner("Analyzing options..."):
            positions = ib.positions()
            option_positions = [p for p in positions if p.contract.secType == 'OPT']

            if not option_positions:
                st.info("No option positions to analyze")
            else:
                analysis_data = []

                for pos in option_positions:
                    contract = pos.contract

                    # Get underlying price
                    stock = Stock(contract.symbol, 'SMART', 'USD')
                    ib.qualifyContracts(stock)

                    ib.reqMarketDataType(3)
                    ticker = ib.reqMktData(stock, '', False, False)
                    time.sleep(1)

                    current_price = None
                    if ticker.last and ticker.last > 0:
                        current_price = ticker.last
                    elif ticker.close and ticker.close > 0:
                        current_price = ticker.close

                    if current_price:
                        # Determine ITM/OTM
                        if contract.right == 'C':  # CALL
                            itm = current_price > contract.strike
                            itm_amount = current_price - contract.strike if itm else 0
                        else:  # PUT
                            itm = current_price < contract.strike
                            itm_amount = contract.strike - current_price if itm else 0

                        analysis_data.append({
                            'Symbol': contract.symbol,
                            'Local Symbol': contract.localSymbol,
                            'Strike': f"${contract.strike:.2f}",
                            'Type': contract.right,
                            'Expiry': contract.lastTradeDateOrContractMonth,
                            'Position': pos.position,
                            'Current Price': f"${current_price:.2f}",
                            'Status': '🟢 ITM' if itm else '🔴 OTM',
                            'ITM Amount': f"${itm_amount:.2f}" if itm else "$0.00"
                        })

                if analysis_data:
                    df_analysis = pd.DataFrame(analysis_data)
                    st.dataframe(df_analysis, use_container_width=True, hide_index=True)

                    # Count ITM options
                    itm_count = sum(1 for row in analysis_data if '🟢 ITM' in row['Status'])
                    if itm_count > 0:
                        st.warning(f"⚠️ You have {itm_count} option(s) in the money!")
                    else:
                        st.success("✅ All options are out of the money")

    except Exception as e:
        st.error(f"Error analyzing options: {e}")

# Footer
st.divider()
st.caption("💡 Trading Bot Dashboard v1.0 | Refresh page to update data | Auto-refresh available in sidebar")
