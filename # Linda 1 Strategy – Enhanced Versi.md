# Linda 1 Strategy – Enhanced Version (v2.0)

This upgraded version of the **Linda 1 strategy** incorporates volatility-based strike targeting, dynamic sizing, hedging options, early-exit automation, and diversification. The goal is to increase safety, consistency, and scalability while retaining the core weekly income model.

---

## 🧠 Strategy Purpose

Sell weekly **out-of-the-money (OTM) PUT options** on high-liquidity stocks (e.g., NVDA, AMD) to capture time decay (theta) while minimizing assignment risk using volatility-aware entry, sizing, and management rules.

---

## 🔁 Weekly Workflow (Upgraded)

1. **Select ticker(s):** NVDA + 1–2 additional liquid tickers (e.g., AMD, META)
2. **Fetch volatility metrics:**
   - Implied Volatility (IV)
   - IV Rank
   - Expected Move (EM) = Price × IV × √(T/365)
3. **Determine entry strike:**
   - Target strike just beyond –1σ or just outside expected move
4. **Adjust contract size:**
   - Use 50–70% of buying power
   - Scale DOWN if IV Rank > 70
5. **Enter trade:**
   - Sell PUT(s) for Friday expiry
   - Use spread if VIX > 20 or high event risk (see Hedging below)
6. **Automated Exit:**
   - Close trade if 80–90% premium is captured
   - Or delta drops below 0.10
7. **Adjust / Roll if price nears strike:**
   - Roll down/out if breach risk appears
8. **If assigned:**
   - Sell shares premarket or write covered call

---

## 🧮 Entry Criteria

| Rule           | Threshold                    |
|----------------|------------------------------|
| IV Rank        | > 25%                        |
| Option Delta   | 0.15–0.25                    |
| Strike Distance| > 1σ or > Expected Move      |
| Premium        | > $1 per contract or >0.5%   |

---

## 📉 Exit & Adjustment Logic

| Trigger              | Action                  |
|----------------------|--------------------------|
| Premium drops 80–90% | Close position early     |
| Delta < 0.10         | Take profit              |
| Price breaches strike| Roll or accept assignment|
| Assigned             | Sell shares or covered call |

---

## 🛡 Hedging & Safety

| Condition           | Strategy                         |
|---------------------|----------------------------------|
| High IV Rank > 70   | Reduce size or use vertical spreads |
| VIX > 20            | Use PUT spreads                   |
| Major event week    | Use < 50% of buying power         |
| Multi-ticker trades | Avoid correlated tickers          |

---

## 📊 Position Sizing Formula (Python-style)

```python
allocation_pct = 0.6 - (iv_rank / 100) * 0.3
buying_power_to_use = total_buying_power * allocation_pct
```

---

## 🧪 Ticker Examples for Diversification

| Ticker | Sector     | Comment                       |
|--------|------------|-------------------------------|
| NVDA   | Semiconductors | Core ticker, highly liquid |
| AMD    | Semiconductors | Correlated with NVDA       |
| META   | Tech        | Strong options liquidity     |
| SHOP   | E-Commerce  | Higher IV                    |
| TSLA   | Auto/Tech   | Use spreads (high volatility)|
| AMZN   | Tech/Retail | Stable large-cap             |

---

## 🤖 Automation Ideas

- Use `ib_insync` to:
  - Fetch IV and option chains
  - Calculate expected move
  - Auto-place limit orders
- Build a FastAPI or CLI tool that:
  - Takes ticker, IV rank, target delta
  - Recommends strike & size
  - Submits order to IBKR

---

## 🔐 Cost Reminders

| Feature               | Cost                        |
|------------------------|-----------------------------|
| IBKR API access        | ✅ Free                     |
| Market data (OPRA + US bundle) | ~$11.50/month (often waived) |
| Option trade commission| ~$0.65 per contract         |
| Paper trading          | ✅ Free                     |

---

## ✅ Final Notes

- This version of Linda 1 adds more **precision**, **safety**, and **scalability**
- Designed to perform in both stable and high-volatility environments
- Easy to scale up with automation or multi-ticker rotation

