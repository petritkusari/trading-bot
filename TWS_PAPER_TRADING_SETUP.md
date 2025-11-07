# TWS PAPER TRADING SETUP - START PRACTICING NOW

**Goal:** Get you connected to TWS Paper Trading in the next 10-15 minutes so you can practice the weekly strategy risk-free.

---

## 🎯 WHAT IS PAPER TRADING?

**Paper trading = Fake money, real market data, real practice**

- Trade with $1,000,000 virtual cash (default)
- Real-time market data
- Same TWS interface as live trading
- Practice without risk
- No money lost if you make mistakes

**You MUST paper trade for 2-4 weeks before using real money!**

---

## 🚀 STEP-BY-STEP: CONNECT TO PAPER TRADING

### **Option 1: If You Already Have an IBKR Live Account**

If you already opened a live Interactive Brokers account:

#### **Step 1: Get Your Paper Trading Username**

Your paper trading username is automatically created when you open an IBKR account.

**Format:**
```
Live account: U1234567
Paper account: DU1234567 (same number with "D" prefix)
```

The **password is the SAME** as your live account.

#### **Step 2: Download/Open TWS**

1. If not installed, download from: https://www.interactivebrokers.com/en/trading/tws.php
2. Install TWS (takes 5-10 minutes)
3. Open TWS from your desktop

#### **Step 3: Login to Paper Trading**

At the login screen:

```
┌─────────────────────────────────────┐
│  Interactive Brokers Login          │
├─────────────────────────────────────┤
│  Username: DU1234567                │ ← Your paper account (D prefix)
│  Password: ••••••••                 │ ← Same as live account
│                                      │
│  Trading Mode:                       │
│  ○ Live Trading                     │
│  ● Paper Trading  ← SELECT THIS     │
│                                      │
│  [ Login ]                          │
└─────────────────────────────────────┘
```

**CRITICAL:** Make sure **"Paper Trading"** is selected!

**2-Factor Authentication:**
- You'll get a code on your phone/email
- Enter it
- Check "Trust this device for 30 days" (convenient)

#### **Step 4: Verify You're in Paper Mode**

After login, check TOP of TWS window:

```
Paper Trading Mode - Account: DU1234567 - $1,000,000.00
```

**If you see "Paper Trading Mode" - YOU'RE GOOD! ✅**

**If you DON'T see it - STOP IMMEDIATELY! You might be in live mode!**

---

### **Option 2: If You DON'T Have an IBKR Account Yet**

You can STILL practice! IBKR offers paper trading without opening a live account.

#### **Step 1: Register for Paper Trading Only**

**Go to:** https://www.interactivebrokers.com/en/trading/tws-updateable-latest.php

**Scroll down to:** "Try TWS Demo"

**Or direct link:** https://ndcdyn.interactivebrokers.com/Universal/servlet/Registration.formSampleLogin

#### **Step 2: Fill Out Short Registration**

**You'll need:**
- Name
- Email address
- Country
- Phone number (optional)

**Choose:**
- Account type: **Individual**
- Region: **Your country**

**Submit form**

#### **Step 3: Check Your Email**

**Within 5 minutes, you'll receive:**
```
Subject: Your IB Demo Account Credentials

Username: demo1234567
Password: ABC123xyz

Download TWS: [link]
```

**Save these credentials!**

#### **Step 4: Download & Install TWS**

1. Click link in email (or go to IBKR website)
2. Download TWS installer
3. Run installer
4. Accept defaults
5. Wait 5-10 minutes for installation

#### **Step 5: Login to Demo Account**

1. Open TWS
2. Enter your demo credentials:
   ```
   Username: demo1234567
   Password: ABC123xyz
   Trading Mode: Paper Trading
   ```
3. Click Login

**You're in!**

---

## ✅ STEP 6: VERIFY YOUR SETUP

After logging in, let's make sure everything works:

### **Check 1: Verify Paper Trading Mode**

**Look at the TOP of TWS window:**

Should say:
```
Paper Trading Mode - Account: DU1234567 - Net Liquidation: $1,000,000.00
```

**RED FLAG:** If it says "Live Trading" - STOP! Log out and log back in with paper account.

---

### **Check 2: Verify You Have Buying Power**

**Look at Account Information (usually top-right):**

```
Buying Power: $4,000,000 (with margin)
Cash: $1,000,000
Net Liquidation: $1,000,000
```

**If you see these numbers, you're good!**

---

### **Check 3: Test Market Data**

**Type a symbol in the search box:**

Type: **AAPL** (Apple stock)

**You should see:**
- Real-time price (e.g., $189.45)
- Bid/Ask
- Change %
- Volume

**If you see "No market data" or "Delayed":**
- This is normal for demo accounts
- You get 15-minute delayed data (still good for practice)
- When you open live account, you'll get real-time data

---

### **Check 4: Test Option Chain**

**Let's verify you can see options:**

1. Type **COIN** in symbol search
2. Right-click COIN → **"Option Chain"**
3. Option chain window should open
4. You should see:
   - Multiple expiration dates
   - Puts and Calls
   - Bid/Ask prices
   - Greeks (Delta, Theta, etc.)

**If option chain works - YOU'RE READY TO TRADE!**

---

## 🎓 CONFIGURE YOUR PAPER TRADING WORKSPACE

Let's set up TWS exactly like the live trading setup:

### **Step 1: Create Your Watchlist**

1. **New Window** → **Watchlist**
2. Name it: "Weekly Puts Practice"
3. Add symbols:
   - VXX
   - COIN
   - TSLA
   - QQQ
   - MSTR

### **Step 2: Set Up Option Chain**

1. Right-click any ticker → **Option Chain**
2. Click **Settings** gear icon
3. Configure:
   - ✅ Show weekly expirations
   - ✅ Show Greeks
   - ✅ Strike range: ±10% from price
   - ✅ Show Bid/Ask/Last

### **Step 3: Open Portfolio Monitor**

1. **Account** → **Account Window**
2. Click **Portfolio** tab
3. Add columns:
   - Position
   - Market Value
   - Unrealized P&L
   - Unrealized P&L %
   - Days to Expiration

### **Step 4: Save Your Layout**

**File** → **Save Workspace As** → "Weekly Puts Paper Trading"

**Now you never have to reconfigure!**

---

## 📝 YOUR FIRST PAPER TRADE (RIGHT NOW!)

Let's place your first practice trade. This will take 5 minutes.

### **Trade Example: Sell VXX Puts**

**Why VXX first?**
- Low stock price ($18) = small capital needed
- High liquidity = easy to trade
- Critical for the strategy
- Good practice

---

### **Step 1: Check Current VXX Price**

1. Type **VXX** in search
2. Look at current price (let's say $18.50)

### **Step 2: Open VXX Option Chain**

1. Right-click VXX
2. Select **"Option Chain"**
3. Choose **nearest Friday expiration** (this week)

### **Step 3: Find ATM Put Strike**

Look at the PUTS section:

```
Strike | Bid   | Ask   | Last  | Delta
$17.00 | $0.45 | $0.55 | $0.50 | -0.35
$18.00 | $0.85 | $0.95 | $0.90 | -0.48
$18.50 | $1.10 | $1.25 | $1.18 | -0.51  ← THIS ONE (ATM)
$19.00 | $1.45 | $1.60 | $1.52 | -0.56
```

**Choose $18.50 strike** (closest to current price)

### **Step 4: Place the Order**

1. **Click on the $18.50 strike row**
2. **Right-click** → **Sell** → **Limit Order**

**Order Ticket appears:**
```
Action: SELL TO OPEN  ✅ (Correct!)
Symbol: VXX
Expiration: Nov 8, 2024
Strike: $18.50
Right: PUT
Quantity: 10 (for practice, use 10 contracts)
Order Type: LIMIT
Limit Price: 1.18 (mid-point between $1.10 and $1.25)
Time in Force: DAY
```

### **Step 5: Review & Submit**

**Check everything:**
- ✅ SELL TO OPEN (not buy)
- ✅ PUT (not call)
- ✅ 10 contracts
- ✅ This Friday expiration

**Capital required:**
```
$18.50 × 100 shares × 10 contracts = $18,500
Your paper account: $1,000,000 ✅ (plenty!)
```

**Premium collected:**
```
$1.18 × 100 × 10 = $1,180
Minus commission: $6.50
Net: $1,173.50
```

**Click "Transmit"**

### **Step 6: Order Filled!**

**Within seconds, you should see:**

```
Status: FILLED
Fill Price: $1.18
Contracts: 10
Premium: $1,180.00
Commission: $6.50
Net: $1,173.50
```

**In your Portfolio:**
```
Position: VXX Nov 8 '24 18.50 PUT
Quantity: -10 (negative = you sold)
Market Value: -$1,180
Unrealized P&L: $0.00 (just opened)
Days to Exp: 4
```

**CONGRATULATIONS! You just made your first paper trade! 🎉**

---

## 📊 TRACK YOUR PAPER TRADES

**Create a practice tracking spreadsheet:**

```
| Date  | Ticker | Action | Contracts | Strike | Exp   | Premium | P&L    | Win? |
|-------|--------|--------|-----------|--------|-------|---------|--------|------|
| 11/5  | VXX    | SELL   | 10        | $18.50 | 11/8  | $1,173  | +$1,173| YES  |
| 11/5  | COIN   | SELL   | 5         | $68    | 11/8  | $1,675  | TBD    | TBD  |
| 11/6  | VXX    | SELL   | 10        | $19    | 11/9  | $1,250  | TBD    | TBD  |
```

**Track:**
- Every trade you make
- Premiums collected
- Final P&L
- Win/Loss
- What you learned

**Goal: 10+ successful trades before going live**

---

## 🎯 2-WEEK PAPER TRADING PLAN

Here's your practice schedule:

### **Week 1: Learning the Basics**

**Monday:**
- [ ] Login to paper account
- [ ] Set up workspace
- [ ] Place 1 VXX trade (daily expiration)
- [ ] Record in spreadsheet
- **Time: 30 minutes**

**Tuesday:**
- [ ] Check Monday's VXX position
- [ ] Place new VXX trade (tomorrow expiration)
- [ ] Add 1 COIN trade (Friday expiration)
- **Time: 20 minutes**

**Wednesday:**
- [ ] Monitor positions
- [ ] Place VXX daily trade
- [ ] Try 1 TSLA trade (Friday)
- **Time: 20 minutes**

**Thursday:**
- [ ] Place VXX daily trade
- [ ] Review Friday expirations (what will happen?)
- **Time: 15 minutes**

**Friday:**
- [ ] Place VXX daily trade (Monday exp)
- [ ] Watch Friday positions expire
- [ ] Calculate week's profit
- [ ] Note: Win rate, mistakes made, lessons learned
- **Time: 25 minutes**

**Week 1 Goal:**
- 8-10 trades total
- Understand order placement
- Win rate > 80%
- No major mistakes

---

### **Week 2: Building Confidence**

**Monday:**
- [ ] Review Week 1 performance
- [ ] Place VXX daily
- [ ] Place 2-3 weekly trades (COIN, TSLA, QQQ)
- [ ] Practice calculating position sizes
- **Time: 30 minutes**

**Tuesday-Thursday:**
- [ ] Daily VXX trades
- [ ] Monitor weekly positions
- [ ] Practice reading P&L
- [ ] Try closing a position early (practice mechanics)
- **Time: 15-20 min/day**

**Friday:**
- [ ] VXX daily trade
- [ ] Close/roll positions if needed
- [ ] Calculate week's profit
- [ ] Review: Total profit, win rate, errors
- **Time: 30 minutes**

**Week 2 Goal:**
- 10-15 trades total
- Win rate > 85%
- Comfortable with routine
- No hesitation placing orders
- Ready for real money!

---

## ✅ PAPER TRADING CHECKLIST (Before Going Live)

**Only move to real money when:**

- [ ] **Completed 10+ trades successfully**
- [ ] **Win rate ≥ 85%**
- [ ] **Understand how to:**
  - [ ] Place sell-to-open orders
  - [ ] Set limit prices
  - [ ] Monitor positions
  - [ ] Close positions
  - [ ] Read P&L
  - [ ] Calculate position sizes
  - [ ] Find ATM strikes
  - [ ] Check expiration dates

- [ ] **Made at least 3 mistakes and learned from them**
  - Wrong expiration
  - Wrong strike
  - Wrong quantity
  - Bought instead of sold
  - Etc.

- [ ] **Comfortable with the routine:**
  - [ ] Monday morning trade placement
  - [ ] Daily monitoring
  - [ ] Friday expirations

- [ ] **Profitable in paper account:**
  - [ ] +10% minimum over 2 weeks
  - [ ] Consistent results
  - [ ] Not just luck

- [ ] **Emotionally ready:**
  - [ ] Not stressed by losses
  - [ ] Don't panic when position goes red
  - [ ] Follow the plan mechanically

**If all checked: YOU'RE READY FOR REAL MONEY!**

---

## ⚠️ COMMON PAPER TRADING MISTAKES

### **Mistake 1: "It's fake money, so I'll be aggressive"**

**Problem:** Trading differently than you would with real money.

**Solution:** Treat every paper trade like real money. Use realistic position sizes ($50k total, not $1M).

---

### **Mistake 2: Not tracking trades**

**Problem:** Can't learn from your mistakes if you don't record them.

**Solution:** Create spreadsheet from Day 1. Record EVERYTHING.

---

### **Mistake 3: Quitting after first loss**

**Problem:** First losing trade scares you away.

**Solution:** Losses happen 10-15% of the time. This is normal! Keep going.

---

### **Mistake 4: Over-trading**

**Problem:** Placing 20 trades per day because "it's not real."

**Solution:** Follow the actual strategy (weekly puts, 5-7 positions max).

---

### **Mistake 5: Not practicing the full routine**

**Problem:** Only practice placing trades, not monitoring/closing.

**Solution:** Follow the complete weekly routine (Monday place, daily monitor, Friday close).

---

### **Mistake 6: Skipping to live trading too early**

**Problem:** "I made $10k paper profit in 2 days, I'm ready!"

**Solution:** Paper trade for minimum 2 weeks. Build habits, not just profits.

---

## 🎓 PRACTICE SCENARIOS

Use paper trading to practice specific situations:

### **Scenario 1: Stock Drops Below Strike**

**Setup:**
- Sell COIN $68 puts
- Wait for COIN to drop to $65

**Practice:**
- What's your P&L?
- Should you roll?
- Should you take assignment?
- How do you close at a loss?

**Learn:** How to handle losing positions calmly

---

### **Scenario 2: Position Extremely Profitable**

**Setup:**
- Sell puts on any stock
- Wait for profit to reach 80%+

**Practice:**
- Closing position early
- Calculating if it's worth it
- Redeploying capital

**Learn:** When to take profits early

---

### **Scenario 3: Market Volatility Spike**

**Setup:**
- Watch for VIX to spike above 20

**Practice:**
- Adjusting position sizes
- Switching strikes (ATM vs OTM)
- Increasing premiums

**Learn:** How to adapt to volatility

---

### **Scenario 4: Rolling a Position**

**Setup:**
- Sell puts that go ITM
- Practice rolling out and down

**Practice:**
- Using "Create Rolling Order"
- Calculating net credit
- Adjusting strikes

**Learn:** Advanced position management

---

## 📞 PAPER TRADING SUPPORT

**If you have issues with paper trading:**

**TWS Not Loading:**
- Clear cache: File → Global Configuration → Clear Cache
- Restart TWS
- Reinstall if needed

**Can't See Options:**
- Check market data subscription
- Demo accounts have 15-min delayed data (normal)
- Options should still be visible

**Order Not Filling:**
- Normal! Paper orders sometimes take longer
- Adjust limit price closer to mid-point
- Or use market order (instant fill)

**Want to Reset Paper Account:**
- Contact IBKR support
- They can reset to $1M and clear history
- Useful if you mess up badly

**Technical Issues:**
- IBKR Chat Support: Available in Account Management
- Phone: 1-877-442-2757
- Hours: 24/7

---

## 🚀 READY TO START?

**RIGHT NOW, DO THIS:**

### **Next 15 Minutes:**

1. [ ] If you have IBKR account: Login to TWS with paper credentials (DU prefix)
2. [ ] If you DON'T: Register for demo account at IBKR website
3. [ ] Download/install TWS if needed
4. [ ] Login to paper trading mode
5. [ ] Verify you see "Paper Trading Mode" at top

### **Next 30 Minutes:**

6. [ ] Set up watchlist (VXX, COIN, TSLA, QQQ, MSTR)
7. [ ] Configure option chain settings
8. [ ] Save your workspace layout
9. [ ] Create tracking spreadsheet

### **Next 15 Minutes:**

10. [ ] Place your FIRST paper trade (VXX puts)
11. [ ] Record in spreadsheet
12. [ ] Pat yourself on the back! 🎉

**Total time to be fully set up: ~1 hour**

---

## 🎯 YOUR GOAL

**Over the next 2 weeks:**

- Complete 20-30 paper trades
- Achieve 85%+ win rate
- Build confidence and routine
- Make (and learn from) mistakes
- Prove to yourself the strategy works

**Then:**

- Open live account with real money
- Start with 25% of capital
- Scale up slowly
- Achieve financial freedom

---

## 📁 QUICK LINKS

**Interactive Brokers Paper Trading:**
- Main site: https://www.interactivebrokers.com
- Demo registration: https://ndcdyn.interactivebrokers.com/Universal/servlet/Registration.formSampleLogin
- TWS download: https://www.interactivebrokers.com/en/trading/tws.php
- Support: Chat in Account Management or call 1-877-442-2757

**Related Guides:**
- Full TWS Setup: `C:\Trading\INTERACTIVE_BROKERS_TWS_SETUP_GUIDE.md`
- Strategy Explanation: `C:\Trading\STRATEGY_2_EXPLAINED_SIMPLE.md`
- VXX Deep Dive: `C:\Trading\VXX_EXPLAINED_THE_CRASH_PROFIT_SECRET.md`
- Weekly vs Daily: `C:\Trading\WEEKLY_VS_DAILY_TRADING_ANALYSIS.md`

---

**NOW GO PRACTICE! Your financial future depends on it!** 🚀

**Questions? Issues? Check the troubleshooting section above or review the full TWS setup guide.**

---

*Remember: Everyone starts as a beginner. Paper trading is how professionals learn. Don't skip this step!*
