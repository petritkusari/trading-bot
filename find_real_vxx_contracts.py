"""
Find REAL VXX contracts that actually exist
"""
from ib_insync import *

def main():
    print("=" * 70)
    print("FINDING REAL VXX PUT CONTRACTS")
    print("=" * 70)

    ib = IB()

    try:
        ib.connect('127.0.0.1', 4002, clientId=1)
        print("\n[OK] Connected")

        # Get VXX stock
        vxx = Stock('VXX', 'SMART', 'USD')
        ib.qualifyContracts(vxx)
        print(f"[OK] VXX contract found: {vxx.conId}")

        # Get all option chains
        print("\nGetting option chains...")
        chains = ib.reqSecDefOptParams(vxx.symbol, '', vxx.secType, vxx.conId)

        if not chains:
            print("[ERROR] No option chains found")
            return

        print(f"[OK] Found {len(chains)} chain(s)")

        for chain in chains:
            print(f"\nExchange: {chain.exchange}")
            print(f"Trading Class: {chain.tradingClass}")

            # Show all expirations
            print(f"\nAll available expirations:")
            expirations = sorted(chain.expirations)[:10]  # First 10
            for exp in expirations:
                print(f"  {exp}")

            # Show all strikes
            print(f"\nAll available strikes:")
            strikes = sorted(chain.strikes)
            print(f"  Range: ${strikes[0]} to ${strikes[-1]}")
            print(f"  Total: {len(strikes)} strikes")

            # Show strikes near $18
            nearby = [s for s in strikes if 16 <= s <= 20]
            print(f"\n  Strikes near $18:")
            for s in nearby:
                print(f"    ${s}")

            # Try to get a few real contracts
            print(f"\nTesting specific contracts...")

            # Try first expiration with strikes near 18
            test_exp = expirations[0]

            for test_strike in nearby[:3]:
                try:
                    test_put = Option('VXX', test_exp, test_strike, 'P', chain.exchange)
                    contracts = ib.qualifyContracts(test_put)

                    if contracts:
                        c = contracts[0]
                        print(f"\n  [FOUND] {c.localSymbol}")
                        print(f"    Symbol: {c.symbol}")
                        print(f"    Strike: ${c.strike}")
                        print(f"    Expiry: {c.lastTradeDateOrContractMonth}")
                        print(f"    Exchange: {c.exchange}")
                        print(f"    ConId: {c.conId}")

                        # This is a real contract we can trade!
                        print(f"\n    >>> THIS CONTRACT EXISTS AND CAN BE TRADED <<<")
                        break
                except Exception as e:
                    print(f"  [FAIL] ${test_strike} PUT: {e}")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

    finally:
        ib.disconnect()

if __name__ == "__main__":
    main()
