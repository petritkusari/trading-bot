# IB Gateway Setup Guide

**Switch from TWS to IB Gateway for Stable Automated Trading**

---

## 🎯 Why Switch to IB Gateway?

| Feature | TWS | IB Gateway |
|---------|-----|------------|
| **Memory Usage** | ~1GB | ~200MB |
| **Stability** | Good | Excellent |
| **GUI** | Full interface | Minimal (login only) |
| **For Automation** | Okay | **Ideal** |
| **Startup Time** | 30-60 sec | 10-20 sec |
| **Can view in TWS?** | N/A | ✅ YES! |

**Bottom Line:** IB Gateway is specifically designed for API connections and automated trading.

---

## 📥 Step 1: Download IB Gateway

### **Option A: Already have IBKR account**

1. Go to: https://www.interactivebrokers.com/en/trading/ibgateway-stable.php
2. Click **Download IB Gateway (Stable)**
3. Choose your operating system:
   - Windows: Download `.exe` installer
   - macOS: Download `.dmg` installer
   - Linux: Download installer script

### **Option B: Need to download**

```bash
# Direct download links (stable version):
Windows: https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-windows-x64.exe
macOS: https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-macos-x64.dmg
Linux: https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-linux-x64.sh
```

---

## 🔧 Step 2: Install IB Gateway

### **Windows:**
1. Run the downloaded `.exe` file
2. Click **Next** through the installer
3. Accept the license agreement
4. Choose installation directory (default is fine)
5. Click **Install**
6. Wait for installation to complete
7. Click **Finish**

### **macOS:**
1. Open the `.dmg` file
2. Drag IB Gateway to Applications folder
3. Open Applications → Right-click IB Gateway → Open
4. Click **Open** when macOS warns about unidentified developer (first time only)

### **Linux:**
```bash
chmod +x ibgateway-stable-standalone-linux-x64.sh
./ibgateway-stable-standalone-linux-x64.sh
```

---

## ⚙️ Step 3: Configure IB Gateway for API Access

### **First Launch:**

1. **Launch IB Gateway**
   - Windows: Start Menu → IB Gateway
   - macOS: Applications → IB Gateway
   - Linux: Run from installation directory

2. **Login Screen:**
   - Username: Your paper trading username (e.g., `edemo` or `DU161775`)
   - Password: Your paper trading password
   - Trading Mode: **Paper Trading** (IMPORTANT!)
   - Click **Login**

3. **Configuration Window Opens:**
   - This is the minimal IB Gateway interface
   - No charts, no portfolio view (by design)
   - Just a small window showing connection status

### **Configure API Settings:**

1. **Click "Configure" in the IB Gateway window**
2. **Go to Settings → API → Settings**
3. **Make these changes:**

   ```
   ✅ Enable ActiveX and Socket Clients: CHECKED
   ❌ Read-Only API: UNCHECKED
   ✅ Download open orders on connection: CHECKED
   ✅ Allow connections from localhost only: CHECKED

   Socket Port: 4002 (Paper Trading)
                4001 (Live Trading - when ready)

   Master API client ID: (leave blank)
   ```

4. **Click "OK"**
5. **IB Gateway will say "Configuration changes require restart"**
6. **Click "OK" and restart IB Gateway**

---

## 🔌 Step 4: Verify Port Configuration

### **Port Reference:**

| Mode | Application | Port |
|------|-------------|------|
| Paper | TWS | 7497 |
| Paper | **IB Gateway** | **4002** |
| Live | TWS | 7496 |
| Live | **IB Gateway** | **4001** |

**IMPORTANT:** Your scripts will now connect to port **4002** (instead of 7497)

---

## 🐍 Step 5: Update Your Python Scripts

### **You've already done this!** ✅

Your scripts now use `ib_config.py` which controls the connection.

### **To switch to IB Gateway:**

1. **Open `ib_config.py`**
2. **Change this line:**
   ```python
   USE_IB_GATEWAY = True  # Was False, now True
   ```
3. **Save the file**

**That's it!** All your scripts will now connect to IB Gateway (port 4002).

---

## 🧪 Step 6: Test the Connection

### **Test 1: Basic Connection**

1. **Make sure IB Gateway is running** (you should see the small window)
2. **Make sure `ib_config.py` has `USE_IB_GATEWAY = True`**
3. **Run your test script:**

```bash
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

3. Current Portfolio Positions:
------------------------------------------------------------
   No open positions

...
CONNECTION TEST SUCCESSFUL!
============================================================
```

### **Test 2: Check Config**

```bash
python ib_config.py
```

**Expected output:**
```
Current Configuration:

============================================================
CONNECTION: IB Gateway (Paper Trading)
Host: 127.0.0.1:4002
Client ID: 10
============================================================

Use IB Gateway: True
Port: 4002

To switch:
  - For IB Gateway: Set USE_IB_GATEWAY = True
  - For TWS: Set USE_IB_GATEWAY = False
```

---

## 👀 Step 7: Monitor in TWS (Optional)

**You can STILL use TWS to view your trades!**

### **Running Both Simultaneously:**

1. **IB Gateway running** (in background, for API connections)
2. **Open TWS** (for visual monitoring)
3. **Login to TWS** with same credentials
4. **See all positions/orders** placed by your Python scripts!

**They both connect to the SAME account!**

### **Workflow:**

```
IB Gateway (background)
├── Python scripts connect here
├── Places trades automatically
└── Always running

TWS (when you want to check)
├── Open to view positions
├── See charts, P&L
├── Manual intervention if needed
└── Close when done monitoring
```

---

## 🔄 Step 8: Auto-Restart (Optional)

IB Gateway can log out after inactivity. To keep it running:

### **Option A: Auto-Restart Script (Windows)**

Create `start_ib_gateway.bat`:
```batch
@echo off
:loop
"C:\Jts\ibgateway\ibgateway.exe"
timeout /t 10
goto loop
```

### **Option B: Scheduled Task (Windows)**

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At log on
4. Action: Start IB Gateway
5. Enable "Restart every 1 hour"

### **Option C: Systemd Service (Linux)**

Create `/etc/systemd/system/ibgateway.service`:
```ini
[Unit]
Description=IB Gateway
After=network.target

[Service]
Type=simple
User=youruser
ExecStart=/opt/ibgateway/ibgateway
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable ibgateway
sudo systemctl start ibgateway
```

---

## ⚠️ Common Issues & Solutions

### **Issue 1: "Connection refused" error**

**Cause:** IB Gateway not running or wrong port

**Solution:**
1. Check IB Gateway window is open
2. Verify port in `ib_config.py` matches Gateway (4002)
3. Restart IB Gateway

### **Issue 2: "Not connected" error**

**Cause:** API not enabled

**Solution:**
1. IB Gateway → Configure → Settings → API → Settings
2. Check "Enable ActiveX and Socket Clients"
3. Uncheck "Read-Only API"
4. Restart IB Gateway

### **Issue 3: Can't see positions in TWS**

**Cause:** Different account or not refreshed

**Solution:**
1. Make sure TWS logged into same account as Gateway
2. TWS → Account → Refresh
3. Wait 5-10 seconds for sync

### **Issue 4: Script connects but orders fail**

**Cause:** Read-Only API still enabled

**Solution:**
1. IB Gateway → Configure → Settings → API → Settings
2. **UNCHECK** "Read-Only API"
3. Click OK and restart Gateway

### **Issue 5: Multiple scripts fail to connect**

**Cause:** Using same clientId

**Solution:**
- Each script needs unique clientId
- Already configured in `ib_config.py`:
  ```python
  CLIENT_IDS = {
      'tws_connect_test': 1,
      'place_vxx_put': 2,
      'place_spy_put': 3,
      # ... etc
  }
  ```

---

## 📊 Quick Reference

### **Daily Workflow:**

```
Morning:
1. Start IB Gateway
2. Verify connection (small window appears)
3. Run: python tws_connect_test.py
4. ✅ If connected, run your trading scripts

During the day:
5. IB Gateway runs in background
6. Open TWS if you want to check positions
7. Scripts execute automatically

Evening:
8. Close TWS (if open)
9. Leave IB Gateway running (or close if done)
```

### **Port Quick Reference:**

| Your Setup | Port |
|------------|------|
| IB Gateway Paper | **4002** ← USE THIS |
| IB Gateway Live | 4001 |
| TWS Paper | 7497 |
| TWS Live | 7496 |

### **File Quick Reference:**

```
Your repo:
├── ib_config.py ← MAIN CONFIG (set USE_IB_GATEWAY = True)
├── tws_connect_test.py ← TEST CONNECTION
├── place_vxx_put_trade.py ← UPDATED
├── place_spy_put_trade.py ← UPDATED
└── ... (all scripts updated)
```

---

## ✅ Success Checklist

Before you start trading with IB Gateway:

- [ ] IB Gateway installed
- [ ] IB Gateway configured (API enabled, port 4002)
- [ ] `ib_config.py` has `USE_IB_GATEWAY = True`
- [ ] `python tws_connect_test.py` runs successfully
- [ ] Connection shows "IB Gateway (Paper Trading)"
- [ ] Can see account info and positions
- [ ] (Optional) Can open TWS and see same data
- [ ] All trading scripts updated to use ib_config
- [ ] Tested placing a paper trade through Gateway

---

## 🎯 Next Steps

1. ✅ **Verify connection:** `python tws_connect_test.py`
2. ✅ **Test trading:** `python place_vxx_put_trade.py` (paper)
3. ✅ **Monitor in TWS:** Open TWS → See position
4. ✅ **Run weekly strategy:** Scripts now use Gateway automatically
5. ✅ **When ready for live:** Change port to 4001 in ib_config.py

---

## 💡 Pro Tips

1. **Keep IB Gateway running 24/7** for automated trading
2. **Use TWS for manual monitoring** (open when needed)
3. **Never change port directly in scripts** - use ib_config.py
4. **Each script has unique clientId** - prevents conflicts
5. **Paper trade for 2+ weeks** before going live
6. **Set up auto-restart** if running unattended

---

## 📞 Support

**If IB Gateway won't connect:**
1. Check this guide's troubleshooting section
2. Verify TWS works (to rule out account issues)
3. Check IB Gateway logs: `~/.ib/logs/` or `C:\Jts\logs\`
4. IBKR Support: https://www.interactivebrokers.com/en/support/

**If scripts don't work:**
1. Verify `ib_config.py` settings
2. Check IB Gateway is running
3. Test with `tws_connect_test.py` first
4. Check error messages (they usually explain the issue)

---

**You're now ready to use IB Gateway for stable, automated trading!** 🚀

**Next:** Run `python tws_connect_test.py` to verify everything works.
