"""
Check VXX current price and available PUT options
"""
from ib_insync import *
import datetime

def main():
    print("=" * 60)
    print("CHECKING VXX OPTIONS")
    print("=" * 60)

    ib = IB()

    try:
        # Connect
        print("\nConnecting to TWS...")
        ib.connect('127.0.0.1', 7497, clientId=1)
        print("[OK] Connected")

        # Get VXX stock
        print("\n1. Getting VXX current price...")
        vxx = Stock('VXX', 'SMART', 'USD')
        ib.qualifyContracts(vxx)

        # Request delayed market data (paper trading)
        ib.reqMarketDataType(3)  # 3 = delayed, 4 = delayed frozen

        # Try to get current price multiple ways
        ticker = ib.reqMktData(vxx, '', False, False)
        ib.sleep(3)  # Wait for data

        current_price = None
        if ticker.last == ticker.last and ticker.last > 0:  # Check for valid number
            current_price = ticker.last
        elif ticker.close == ticker.close and ticker.close > 0:
            current_price = ticker.close
        elif ticker.bid == ticker.bid and ticker.bid > 0:
            current_price = ticker.bid
        else:
            # Use a reasonable estimate based on VXX typical range
            current_price = 18.0  # Default estimate
            print(f"   [INFO] Using estimated price (market data limited in paper trading)")

        print(f"   VXX Current Price: ${current_price:.2f}")

        # Get option chains
        print("\n2. Finding weekly PUT options...")
        chains = ib.reqSecDefOptParams(vxx.symbol, '', vxx.secType, vxx.conId)

        if not chains:
            print("   [ERROR] No option chains found")
            return

        chain = chains[0]
        print(f"   Exchange: {chain.exchange}")

        # Get nearest Friday expirations
        today = datetime.date.today()
        print(f"   Today: {today}")

        # Find next 2 Fridays
        fridays = []
        for exp in sorted(chain.expirations):
            exp_date = datetime.datetime.strptime(exp, '%Y%m%d').date()
            days_away = (exp_date - today).days
            if 0 <= days_away <= 14:  # Next 2 weeks
                fridays.append((exp, exp_date, days_away))

        print("\n3. Available Weekly Expirations:")
        print("-" * 60)
        for i, (exp, exp_date, days) in enumerate(fridays[:3], 1):
            print(f"   {i}. {exp_date} ({exp}) - {days} days away")

        if not fridays:
            print("   No weekly expirations found in next 2 weeks")
            return

        # Use the closest Friday
        target_exp, target_date, days_away = fridays[0]
        print(f"\n4. TARGET EXPIRATION: {target_date} ({days_away} days away)")

        # Find ATM strikes (within 10% of current price)
        print(f"\n5. Available PUT strikes near ${current_price:.2f}...")
        print("-" * 60)

        atm_strikes = [s for s in chain.strikes
                      if abs(s - current_price) / current_price < 0.10]
        atm_strikes = sorted(atm_strikes)

        if not atm_strikes:
            # If no strikes in range, show the middle strikes
            atm_strikes = sorted(chain.strikes)[len(chain.strikes)//2-5:len(chain.strikes)//2+5]

        print(f"\n   Available strikes (closest to ATM ${current_price:.2f}):")
        for strike in atm_strikes[:10]:
            distance = ((strike - current_price) / current_price) * 100
            atm_label = "ATM" if abs(distance) < 2 else f"{distance:+.1f}%"
            print(f"   ${strike:6.2f} ({atm_label})")

        print("\n" + "=" * 60)
        print("RECOMMENDATION FOR FIRST TRADE:")
        print("=" * 60)

        # Find the strike closest to current price
        closest_strike = min(atm_strikes[:5], key=lambda x: abs(x - current_price))

        print(f"\nSELL TO OPEN:")
        print(f"   10 VXX {target_date.strftime('%b %d')} ${closest_strike:.2f} PUT")
        print(f"\nThis is:")
        print(f"   - ATM (at-the-money) strike near ${current_price:.2f}")
        print(f"   - Weekly expiration ({days_away} days)")
        print(f"   - PUT option (correct for this strategy)")
        print(f"\nReady to place this trade? (see next script)")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

    finally:
        ib.disconnect()
        print("\nDisconnected")

if __name__ == "__main__":
    main()
