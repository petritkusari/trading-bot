"""
Check order status and current SPY option prices
"""
from ib_insync import *

def main():
    print("=" * 70)
    print("CHECKING ORDER STATUS AND SPY OPTION PRICES")
    print("=" * 70)

    ib = IB()

    try:
        ib.connect('127.0.0.1', 7497, clientId=1)
        print("\n[OK] Connected\n")

        # Check all open orders
        print("1. OPEN ORDERS:")
        print("-" * 70)
        trades = ib.openTrades()

        if trades:
            for i, trade in enumerate(trades, 1):
                print(f"\nOrder #{i}:")
                print(f"  Symbol: {trade.contract.symbol}")
                if hasattr(trade.contract, 'right'):
                    print(f"  Contract: {trade.contract.localSymbol}")
                    print(f"  Strike: ${trade.contract.strike}")
                    print(f"  Expiry: {trade.contract.lastTradeDateOrContractMonth}")
                    print(f"  Type: {trade.contract.right}")
                print(f"  Action: {trade.order.action}")
                print(f"  Quantity: {trade.order.totalQuantity}")
                print(f"  Order Type: {trade.order.orderType}")
                if hasattr(trade.order, 'lmtPrice') and trade.order.lmtPrice:
                    print(f"  Limit Price: ${trade.order.lmtPrice}")
                print(f"  Status: {trade.orderStatus.status}")
                print(f"  Filled: {trade.orderStatus.filled}")
                print(f"  Remaining: {trade.orderStatus.remaining}")
        else:
            print("  No open orders")

        # Check filled positions
        print("\n2. FILLED POSITIONS:")
        print("-" * 70)
        positions = ib.positions()

        if positions:
            for pos in positions:
                print(f"\n  {pos.contract.localSymbol if hasattr(pos.contract, 'localSymbol') else pos.contract.symbol}")
                print(f"  Position: {pos.position}")
                print(f"  Avg Cost: ${pos.avgCost:.2f}")
        else:
            print("  No filled positions")

        # Get current SPY price
        print("\n3. CURRENT SPY PRICE:")
        print("-" * 70)
        spy = Stock('SPY', 'SMART', 'USD')
        ib.qualifyContracts(spy)

        ib.reqMarketDataType(3)  # Delayed
        ticker = ib.reqMktData(spy, '', False, False)
        ib.sleep(2)

        current_price = ticker.last if ticker.last == ticker.last else ticker.close
        print(f"  SPY: ${current_price:.2f}")

        # Check Nov 7 673 PUT bid/ask
        print("\n4. SPY NOV 07 '25 673 PUT - CURRENT BID/ASK:")
        print("-" * 70)

        put_nov7 = Option('SPY', '20251107', 673, 'P', 'SMART')
        contracts = ib.qualifyContracts(put_nov7)

        if contracts:
            put = contracts[0]
            ticker = ib.reqMktData(put, '', False, False)
            ib.sleep(2)

            bid = ticker.bid if ticker.bid == ticker.bid else 0
            ask = ticker.ask if ticker.ask == ticker.ask else 0
            last = ticker.last if ticker.last == ticker.last else 0

            print(f"  Contract: {put.localSymbol}")
            print(f"  BID: ${bid:.2f} <- You get this price when SELLING")
            print(f"  ASK: ${ask:.2f}")
            print(f"  LAST: ${last:.2f}")
            print(f"  Spread: ${ask - bid:.2f}")

            print(f"\n  Your limit order: $2.50")
            if bid > 0:
                if bid >= 2.50:
                    print(f"  ✓ Should fill! Bid (${bid:.2f}) >= Your limit ($2.50)")
                else:
                    print(f"  ✗ Won't fill yet. Bid (${bid:.2f}) < Your limit ($2.50)")
                    print(f"  SOLUTION: Lower your limit to ${bid:.2f} or use MARKET order")
            else:
                print(f"  ? No bid data available (paper trading limitation)")
                print(f"  SOLUTION: Try using MARKET order instead of LIMIT")
        else:
            print("  Could not find contract")

        print("\n" + "=" * 70)
        print("RECOMMENDATIONS:")
        print("=" * 70)
        print("\n1. For manual order:")
        print("   - Check the current BID price above")
        print("   - If BID < $2.50, modify your limit price to match BID")
        print("   - OR change to MARKET order for immediate fill")

        print("\n2. For API order (Nov 5 expiry):")
        print("   - That's expiring TODAY in a few hours")
        print("   - Paper trading might not fill same-day expirations")
        print("   - Can cancel that one and focus on Nov 7 order")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

    finally:
        ib.disconnect()

if __name__ == "__main__":
    main()
