# Using IB Gateway + TWS Together (Recommended Setup)

**Best of both worlds: Automation + Visual Monitoring**

---

## 🎯 The Perfect Setup

```
┌─────────────────────────────────────────────────────────┐
│  IB Gateway (Background - Always Running)               │
│  ├── Port 4002 (Paper Trading)                          │
│  ├── Python scripts connect here                        │
│  ├── Handles automated trading                          │
│  ├── Low memory (~200MB)                                │
│  └── Stable for 24/7 operation                          │
└─────────────────────────────────────────────────────────┘
                          ↓
                  [SAME ACCOUNT]
                          ↓
┌─────────────────────────────────────────────────────────┐
│  TWS (When You Want to Check)                           │
│  ├── Full visual interface                              │
│  ├── See positions placed by scripts                    │
│  ├── Charts, P&L, portfolio                             │
│  ├── Manual trading if needed                           │
│  └── Close when done monitoring                         │
└─────────────────────────────────────────────────────────┘
```

**Both connect to the SAME account and show SAME data in real-time!**

---

## ✅ Setup Steps (10 Minutes Total)

### **Step 1: Download & Install IB Gateway** (5 min)

**Windows:**
```
1. Download: https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-windows-x64.exe
2. Run the installer
3. Click through installation (default settings are fine)
4. Done!
```

**macOS/Linux:** See `IB_GATEWAY_SETUP_GUIDE.md`

---

### **Step 2: Configure IB Gateway** (3 min)

**First time launch:**

1. **Start IB Gateway**
   - Windows: Start Menu → IB Gateway
   - You'll see a login window

2. **Login:**
   - Username: Your paper trading username (same as TWS)
   - Password: Your paper trading password (same as TWS)
   - Trading Mode: **Paper Trading**
   - Click **Login**

3. **Configure API (CRITICAL!):**
   - Small Gateway window appears
   - Click **Configure** button
   - Go to: **Settings → API → Settings**
   - Make these changes:
     ```
     ✅ Enable ActiveX and Socket Clients: CHECKED
     ❌ Read-Only API: UNCHECKED (important!)

     Socket Port: 4002 (paper trading)
     ```
   - Click **OK**
   - Click **OK** again when it asks to restart
   - **Close IB Gateway** and **restart it**

4. **Verify:**
   - IB Gateway should now be running
   - Small window showing "IB Gateway" at the top
   - Status: "Connected"

---

### **Step 3: Verify Your Config** (1 min)

Your scripts are already configured! Just verify:

```bash
# Check current config
python ib_config.py
```

**Expected output:**
```
============================================================
CONNECTION: IB Gateway (Paper Trading)
Host: 127.0.0.1:4002
============================================================

Use IB Gateway: True
Port: 4002
```

✅ If you see this, you're good!

❌ If it shows TWS, edit `ib_config.py`:
```python
USE_IB_GATEWAY = True  # Set to True
```

---

### **Step 4: Test Connection** (1 min)

```bash
# Test IB Gateway connection
python tws_connect_test.py
```

**Expected output:**
```
============================================================
CONNECTION: IB Gateway (Paper Trading)
Host: 127.0.0.1:4002
Client ID: 1
============================================================

1. Attempting connection to 127.0.0.1:4002...
[OK] CONNECTED SUCCESSFULLY!

2. Checking account information...
   Accounts: ['DU161775']

CONNECTION TEST SUCCESSFUL!
```

✅ **Success!** Your scripts now connect to IB Gateway!

---

## 👀 Using TWS to Monitor (While Gateway is Running)

### **Opening TWS for Visual Monitoring:**

**While IB Gateway is running:**

1. **Launch TWS** (regular Trader Workstation)
   - Open TWS application
   - Login with **SAME credentials** as Gateway
   - Select **Paper Trading** mode

2. **You'll see EVERYTHING:**
   - All positions placed by your scripts
   - All orders (open and filled)
   - Your portfolio value
   - P&L in real-time
   - Charts, market data, etc.

3. **What you can do in TWS:**
   - ✅ View all positions
   - ✅ See charts and analytics
   - ✅ Monitor P&L
   - ✅ Manually place trades (if needed)
   - ✅ Cancel orders placed by scripts
   - ✅ Close positions
   - ✅ Everything you normally do in TWS!

4. **When you're done:**
   - Just close TWS
   - IB Gateway keeps running
   - Your scripts keep working

---

## 🔄 Daily Workflow Example

### **Morning (Start of Day):**
```bash
# 1. Start IB Gateway (if not already running)
#    - Launch IB Gateway → Login → Minimize

# 2. Test connection
python tws_connect_test.py

# 3. Run your trading strategy
python place_vxx_put_trade.py
```

### **During the Day:**
```
IB Gateway: Running in background
Your scripts: Can run anytime (scheduled or manual)
TWS: Closed (not needed)
```

### **When You Want to Check Positions:**
```
1. Open TWS
2. Login with same credentials
3. See all your positions and P&L
4. Close TWS when done
5. IB Gateway keeps running
```

### **Evening:**
```
Option A: Leave IB Gateway running (recommended for automation)
Option B: Close everything if you're done for the day
```

---

## 🔄 Switching Between Gateway and TWS

**Need to use TWS instead of Gateway for your scripts?**

Just edit `ib_config.py`:

```python
# Use IB Gateway (default - recommended)
USE_IB_GATEWAY = True

# Switch to TWS (if needed)
USE_IB_GATEWAY = False
```

**All scripts automatically switch!** No need to edit each script.

---

## 💡 Real-World Example

**Scenario:** Monday morning, you want to place weekly puts

### **Setup 1: IB Gateway + Scripts (Automation)**

```bash
# IB Gateway is running in background

# Run your script
python place_vxx_put_trade.py
```

**Output:**
```
============================================================
PLACING VXX PUT TRADE
============================================================
CONNECTION: IB Gateway (Paper Trading)
Host: 127.0.0.1:4002

1. Connecting to IB Gateway (Paper Trading)...
   [OK] Connected to Paper Trading

2. Creating PUT contract...
   [OK] Contract qualified: VXX 251107P18

3. Creating SELL TO OPEN order...
   Order Details:
   Action:    SELL TO OPEN
   Quantity:  10 contracts
   Symbol:    VXX
   Strike:    $18.00

Do you want to TRANSMIT this order? (yes/no): yes

5. Transmitting order...
   [OK] Order transmitted!
   Status: Filled

CONGRATULATIONS! FIRST TRADE PLACED!
```

### **Setup 2: Open TWS to Monitor (Optional)**

While Gateway is still running:

```
1. Launch TWS
2. Login (same credentials)
3. Go to Portfolio window
4. See your new position:

   Symbol: VXX
   Position: -10
   Description: VXX Nov 7 '25 18 PUT
   Market Value: -$1,150
   Unrealized P&L: +$50
```

**Both showing the same position!**

---

## ⚠️ Important Notes

### **Can Both Run Simultaneously?**
✅ **YES!** IB Gateway and TWS can both be open at the same time.

### **Which One Do Scripts Use?**
📍 **Controlled by `ib_config.py`**
- `USE_IB_GATEWAY = True` → Scripts connect to Gateway (port 4002)
- `USE_IB_GATEWAY = False` → Scripts connect to TWS (port 7497)

### **Can I Trade Manually in TWS While Gateway is Running?**
✅ **YES!** Any trades you place in TWS will be visible to your scripts and vice versa.

### **What if Both Are Closed?**
❌ Scripts will fail with "Connection refused" error. At least one must be running.

### **Which One Should I Leave Running?**
📍 **IB Gateway** - It's lighter and more stable for 24/7 operation.
📍 **TWS** - Only open when you need visual monitoring.

---

## 🧪 Quick Test: Verify Both Work

### **Test 1: IB Gateway Connection**
```bash
# Make sure IB Gateway is running
# Make sure ib_config.py has USE_IB_GATEWAY = True

python tws_connect_test.py
```

**Should show:** `CONNECTION: IB Gateway (Paper Trading)`

### **Test 2: TWS Viewing**
```bash
# 1. Run test above (places connection via Gateway)
# 2. Open TWS (login with same credentials)
# 3. Check Portfolio window
# 4. You should see same account info
```

### **Test 3: Switch to TWS**
```bash
# 1. Edit ib_config.py → USE_IB_GATEWAY = False
# 2. Close IB Gateway
# 3. Open TWS
# 4. Run: python tws_connect_test.py
```

**Should show:** `CONNECTION: TWS (Paper Trading)`

### **Test 4: Switch Back to Gateway**
```bash
# 1. Edit ib_config.py → USE_IB_GATEWAY = True
# 2. Close TWS
# 3. Open IB Gateway
# 4. Run: python tws_connect_test.py
```

**Should show:** `CONNECTION: IB Gateway (Paper Trading)`

---

## 📋 Troubleshooting

### **"Connection refused" error**

**Check:**
1. Is IB Gateway running? (you should see the small window)
2. Is `ib_config.py` set to `USE_IB_GATEWAY = True`?
3. Did you configure API in Gateway settings?
4. Did you restart Gateway after configuring?

### **TWS doesn't show positions placed by scripts**

**Fix:**
1. Make sure TWS logged into same account as Gateway
2. In TWS: Right-click Account → Refresh
3. Wait 5-10 seconds for data to sync

### **Can't run scripts while TWS is open**

**This is fine!** You can:
- Close TWS and run scripts via Gateway
- OR change `ib_config.py` to `USE_IB_GATEWAY = False` and use TWS

### **Both Gateway and TWS are running, which does my script use?**

**Controlled by `ib_config.py`:**
- `USE_IB_GATEWAY = True` → Uses Gateway (port 4002)
- `USE_IB_GATEWAY = False` → Uses TWS (port 7497)

Check with:
```bash
python ib_config.py
```

---

## ✅ Recommended Workflow

**For maximum flexibility:**

1. **Install both IB Gateway and TWS** (you already have TWS)
2. **Set up IB Gateway** (10 minutes, one-time)
3. **Default to Gateway** (`USE_IB_GATEWAY = True`)
4. **Run scripts via Gateway** (automated trading)
5. **Open TWS when needed** (visual monitoring)
6. **Switch to TWS if needed** (edit `ib_config.py`)

**You have complete flexibility!**

---

## 🎯 Summary

| Feature | IB Gateway | TWS | Both |
|---------|-----------|-----|------|
| **For Scripts** | ✅ Recommended | ✅ Works | ✅ Choose in config |
| **Visual Monitor** | ❌ No GUI | ✅ Full interface | ✅ Use TWS |
| **Stability** | ✅ Excellent | ✅ Good | ✅ Gateway better |
| **Memory** | ✅ 200MB | ⚠️ 1GB | ✅ Gateway lighter |
| **24/7 Operation** | ✅ Ideal | ⚠️ OK | ✅ Gateway better |

**Best Setup:** Gateway for automation + TWS for monitoring

---

## 🚀 Next Steps

1. **Install IB Gateway** (if not done yet)
2. **Configure API settings** (critical!)
3. **Test connection:** `python tws_connect_test.py`
4. **Run your first trade:** `python place_vxx_put_trade.py`
5. **Open TWS to see it** (optional)
6. **Enjoy the flexibility!**

---

**You now have the best of both worlds!** 🎉

**Questions?** Check:
- Full setup: `IB_GATEWAY_SETUP_GUIDE.md`
- Quick start: `MIGRATION_TO_IB_GATEWAY.md`
- Config reference: `ib_config.py`
