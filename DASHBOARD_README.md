# Trading Dashboard - Setup Instructions

## The Issue
There's a Windows SSL certificate store issue preventing Streamlit from starting in Git Bash.

## Solution 1: Run from Windows Command Prompt (RECOMMENDED)

1. Open **Windows Command Prompt** (cmd.exe):
   - Press `Win + R`
   - Type `cmd`
   - Press Enter

2. Navigate to the Trading folder:
   ```
   cd C:\Trading
   ```

3. Run the dashboard:
   ```
   streamlit run trading_dashboard.py
   ```

4. Your browser will automatically open to: http://localhost:8501

**This usually works because Windows Command Prompt handles SSL certificates differently than Git Bash.**

---

## Solution 2: Run from PowerShell

1. Open **PowerShell**
2. Run:
   ```powershell
   cd C:\Trading
   streamlit run trading_dashboard.py
   ```

---

## Dashboard Features

Once running, you'll have access to:

- 💰 **Account Summary** - Real-time account value, P&L, buying power
- 📊 **Current Positions** - All stock and option positions
- 📋 **Open Orders** - Monitor pending orders
- ⚡ **Trade Executor** - Place buy/sell orders with dropdown menus
- 🎯 **Option Analyzer** - Check ITM/OTM status, close positions
- 🔄 **Auto-refresh** - Optional 5-second refresh

---

## How to Use

### Connecting:
1. Make sure IB Gateway or TWS is running
2. Click "Connect to IB Gateway/TWS" in the sidebar
3. Dashboard will show your account info

### Placing Trades:
1. Enter symbol (e.g., TSLA)
2. Select BUY or SELL
3. Enter quantity
4. Choose MARKET or LIMIT order
5. Click "Execute Trade"

### Analyzing Options:
1. Click "Analyze All Options"
2. See which options are ITM/OTM
3. Close positions as needed

---

## Troubleshooting

**"Connection refused"**:
- Make sure IB Gateway/TWS is running
- Check that API is enabled
- Port should be 4002 (Gateway) or 7497 (TWS)

**Dashboard won't start**:
- Try running from Windows Command Prompt (cmd.exe)
- Make sure port 8501 is not in use
- Check that Python and Streamlit are installed

---

## Alternative: Flask Dashboard

If Streamlit continues to have SSL issues, we have a Flask-based dashboard ready as backup.
Flask is simpler and doesn't have SSL certificate issues.

Ask me to build the Flask version if needed!
