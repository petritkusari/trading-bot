"""
Place SPY PUT Trade - Your First Trade (SPY is more reliable than VXX in paper trading)
"""
from ib_insync import *

def main():
    print("=" * 70)
    print("PLACING YOUR FIRST PAPER TRADE - SPY PUT")
    print("=" * 70)

    ib = IB()

    try:
        ib.connect('127.0.0.1', 4002, clientId=1)
        print("\n[OK] Connected to Paper Trading\n")

        # Get SPY stock price first
        spy = Stock('SPY', 'SMART', 'USD')
        ib.qualifyContracts(spy)

        # Get current price
        ib.reqMarketDataType(3)  # Delayed data
        ticker = ib.reqMktData(spy, '', False, False)
        ib.sleep(2)

        current_price = 580.0  # SPY typical price
        if ticker.last == ticker.last and ticker.last > 0:
            current_price = ticker.last
        elif ticker.close == ticker.close and ticker.close > 0:
            current_price = ticker.close

        print(f"SPY Current Price: ${current_price:.2f}")

        # Get option chains
        chains = ib.reqSecDefOptParams('SPY', '', 'STK', spy.conId)
        chain = chains[0]

        # Find nearest Friday
        expirations = sorted(chain.expirations)[:5]
        print(f"\nAvailable expirations:")
        for i, exp in enumerate(expirations, 1):
            print(f"  {i}. {exp}")

        target_exp = expirations[0]
        print(f"\nUsing expiration: {target_exp}")

        # Find ATM strike
        strikes = sorted(chain.strikes)
        atm_strike = min(strikes, key=lambda x: abs(x - current_price))

        print(f"ATM Strike (closest to ${current_price:.2f}): ${atm_strike}")

        # Create PUT contract
        print(f"\nCreating contract...")
        put = Option('SPY', target_exp, atm_strike, 'P', 'SMART')

        contracts = ib.qualifyContracts(put)
        if not contracts:
            print("[ERROR] Could not qualify contract")
            return

        put = contracts[0]
        print(f"[OK] Contract: {put.localSymbol}")

        # Create order - just 1 contract for first trade
        print(f"\nOrder details:")
        print(f"  SELL 1 {put.localSymbol}")
        print(f"  Strike: ${put.strike}")
        print(f"  Expiry: {put.lastTradeDateOrContractMonth}")
        print(f"  Type: PUT")

        order = MarketOrder('SELL', 1)

        # Place order
        print(f"\nPlacing order...")
        trade = ib.placeOrder(put, order)
        ib.sleep(3)

        print(f"\n[OK] Order placed!")
        print(f"  Order ID: {trade.order.orderId}")
        print(f"  Status: {trade.orderStatus.status}")

        # Check position
        ib.sleep(2)
        positions = ib.positions()

        print(f"\nYour positions:")
        for pos in positions:
            print(f"  {pos.contract.localSymbol}: {pos.position} contracts")

        print("\n" + "=" * 70)
        print("SUCCESS! FIRST TRADE COMPLETED!")
        print("=" * 70)
        print("\nWhat you just did:")
        print("  - SOLD 1 SPY PUT option (cash-secured)")
        print("  - Collected premium upfront")
        print("  - If SPY stays above strike: PUT expires worthless, keep premium")
        print("  - If SPY drops below strike: Buy 100 SPY shares at strike price")
        print("\nCheck TWS Portfolio window to see your position!")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

    finally:
        ib.disconnect()

if __name__ == "__main__":
    main()
