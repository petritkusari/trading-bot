# Migration from TWS to IB Gateway - Quick Guide

**Status:** Scripts Updated ✅
**Next:** Install IB Gateway and test connection

---

## 🎯 What Changed?

### **Before (TWS):**
```python
# Hardcoded in each script
ib.connect('127.0.0.1', 7497, clientId=1)
```

### **After (IB Gateway with Config):**
```python
# Centralized in ib_config.py
from ib_config import get_connection_params
params = get_connection_params('script_name')
ib.connect(params['host'], params['port'], params['clientId'])
```

---

## ✅ Already Completed

Your scripts have been updated:
- ✅ `ib_config.py` created (centralized config)
- ✅ `tws_connect_test.py` updated
- ✅ `place_vxx_put_trade.py` updated
- ✅ All scripts now use config file

---

## 📋 Migration Steps (Do This Now)

### **Step 1: Download IB Gateway** (5 minutes)

**Windows:**
```
1. Go to: https://www.interactivebrokers.com/en/trading/ibgateway-stable.php
2. Download IB Gateway (Stable)
3. Run installer
4. Click through installation
```

**See full guide:** `IB_GATEWAY_SETUP_GUIDE.md`

### **Step 2: Configure IB Gateway** (2 minutes)

1. Launch IB Gateway
2. Login with paper trading credentials
3. Configure → Settings → API → Settings:
   - ✅ Enable ActiveX and Socket Clients
   - ❌ Read-Only API (UNCHECK this!)
   - Port: **4002** (paper trading)
4. Click OK and restart Gateway

### **Step 3: Update Config File** (30 seconds)

**Edit `ib_config.py`:**
```python
# Change this line:
USE_IB_GATEWAY = True  # Set to True (was False)
```

That's it! All scripts will now use IB Gateway.

### **Step 4: Test Connection** (1 minute)

```bash
# Run verification script
python verify_ib_gateway_setup.py
```

**Expected output:**
```
✅ ib_config.py found
✅ Configured for IB Gateway
✅ Connected successfully!
✅ Scripts updated
🎉 READY TO USE IB GATEWAY!
```

### **Step 5: Test Trading Script** (2 minutes)

```bash
python tws_connect_test.py
```

**Should show:**
```
CONNECTION: IB Gateway (Paper Trading)
Host: 127.0.0.1:4002
[OK] CONNECTED SUCCESSFULLY!
```

---

## 🔄 Switching Between TWS and IB Gateway

**It's easy!** Just edit `ib_config.py`:

```python
# For IB Gateway (recommended for automation)
USE_IB_GATEWAY = True

# For TWS (if you need to switch back)
USE_IB_GATEWAY = False
```

All scripts update automatically!

---

## 👀 Viewing Trades in TWS

**You can STILL use TWS for monitoring!**

**Recommended workflow:**
```
IB Gateway (background)
├── Always running
├── Python scripts connect here
└── Places trades automatically

TWS (when you want to check)
├── Open TWS application
├── Login with same credentials
├── See ALL positions placed by scripts!
└── Close when done
```

**Both show the same account data in real-time!**

---

## 📊 Port Reference

| Application | Mode | Port |
|-------------|------|------|
| **IB Gateway** | **Paper** | **4002** ← YOU'LL USE THIS |
| IB Gateway | Live | 4001 |
| TWS | Paper | 7497 |
| TWS | Live | 7496 |

---

## 🔧 Updated Scripts

All these scripts now use `ib_config.py`:

```
✅ tws_connect_test.py - Test connection
✅ place_vxx_put_trade.py - Place VXX puts
✅ place_spy_put_trade.py - Place SPY puts
✅ check_order_status.py - Check orders
✅ cancel_and_place_new.py - Cancel/replace orders
✅ check_vxx_options.py - Check VXX options
✅ find_real_vxx_contracts.py - Find contracts
```

Each script has unique `clientId` to prevent conflicts.

---

## ⚠️ Troubleshooting

### **"Connection refused"**
- Make sure IB Gateway is running (you should see a small window)
- Check `ib_config.py` has `USE_IB_GATEWAY = True`
- Verify port is 4002 in Gateway settings

### **"API not enabled"**
- IB Gateway → Configure → Settings → API → Settings
- Enable "ActiveX and Socket Clients"
- **Uncheck** "Read-Only API"
- Restart Gateway

### **Scripts still try to connect to TWS**
- Check `ib_config.py`:
  ```python
  USE_IB_GATEWAY = True  # Must be True!
  ```
- Save the file
- Run script again

### **Can't see trades in TWS**
- Make sure TWS logged into same account as Gateway
- TWS → Account → Refresh
- Wait 5-10 seconds for data to sync

---

## 🎯 Quick Start Commands

```bash
# 1. Verify setup
python verify_ib_gateway_setup.py

# 2. Test connection
python tws_connect_test.py

# 3. Place test trade
python place_vxx_put_trade.py

# 4. Check status
python check_order_status.py
```

---

## 📚 Documentation

- **Full Setup Guide:** `IB_GATEWAY_SETUP_GUIDE.md`
- **Config File:** `ib_config.py`
- **Verification:** `verify_ib_gateway_setup.py`
- **Original TWS Guide:** `INTERACTIVE_BROKERS_TWS_SETUP_GUIDE.md`

---

## ✅ Migration Checklist

**Complete these in order:**

- [ ] Download IB Gateway
- [ ] Install IB Gateway
- [ ] Configure IB Gateway (API enabled, port 4002)
- [ ] Edit `ib_config.py` → `USE_IB_GATEWAY = True`
- [ ] Run `python verify_ib_gateway_setup.py`
- [ ] Run `python tws_connect_test.py`
- [ ] Verify connection shows "IB Gateway (Paper Trading)"
- [ ] (Optional) Open TWS → See same account
- [ ] Place test trade via script
- [ ] See trade appear in TWS (if open)
- [ ] Start using IB Gateway for all trading!

---

## 💡 Benefits You'll Get

✅ **More stable** - IB Gateway designed for API connections
✅ **Lower memory** - Uses 1/5th the RAM of TWS
✅ **Faster startup** - Launches in 10-20 seconds
✅ **Better for automation** - Can run 24/7 in background
✅ **Still can monitor in TWS** - Open TWS anytime to view positions
✅ **Same account** - Everything syncs in real-time

---

## 🚀 Next Steps

**Right now:**
1. Download IB Gateway (5 min)
2. Configure it (2 min)
3. Update `ib_config.py` (30 sec)
4. Test connection (1 min)

**Total time: ~10 minutes to switch!**

**Then:** Continue with your weekly put-selling strategy using IB Gateway.

---

**Questions?** See `IB_GATEWAY_SETUP_GUIDE.md` for detailed instructions.

**Ready to switch?** Run `python verify_ib_gateway_setup.py` after setup!
