"""
Cancel stuck orders and place fresh SPY PUT with better expiration
"""
from ib_insync import *

def main():
    print("=" * 70)
    print("CANCELING STUCK ORDERS AND PLACING FRESH TRADE")
    print("=" * 70)

    ib = IB()

    try:
        ib.connect('127.0.0.1', 7497, clientId=1)
        print("\n[OK] Connected\n")

        # Cancel all open orders
        print("1. Canceling all pending orders...")
        trades = ib.openTrades()

        if trades:
            for trade in trades:
                print(f"   Canceling: {trade.contract.localSymbol if hasattr(trade.contract, 'localSymbol') else trade.contract.symbol}")
                ib.cancelOrder(trade.order)

            ib.sleep(2)
            print("   [OK] Orders cancelled\n")
        else:
            print("   No orders to cancel\n")

        # Get SPY and find a good expiration
        print("2. Finding SPY options with good liquidity...")
        spy = Stock('SPY', 'SMART', 'USD')
        ib.qualifyContracts(spy)

        # Get option chains
        chains = ib.reqSecDefOptParams('SPY', '', 'STK', spy.conId)
        chain = chains[0]

        # Find expirations (skip today, use Friday or next week)
        expirations = sorted(chain.expirations)
        print(f"   Available expirations:")
        for i, exp in enumerate(expirations[:10], 1):
            print(f"     {i}. {exp}")

        # Use the 3rd expiration (skip today and tomorrow)
        target_exp = expirations[2] if len(expirations) > 2 else expirations[1]
        print(f"\n   Using expiration: {target_exp}")

        # Get current price estimate
        ib.reqMarketDataType(3)
        ticker = ib.reqMktData(spy, '', False, False)
        ib.sleep(2)

        current_price = 673.0  # Default
        if ticker.close == ticker.close and ticker.close > 0:
            current_price = ticker.close

        print(f"   SPY price estimate: ${current_price:.2f}")

        # Find ATM strike
        strikes = sorted(chain.strikes)
        atm_strike = min(strikes, key=lambda x: abs(x - current_price))
        print(f"   ATM Strike: ${atm_strike}")

        # Create PUT contract
        print(f"\n3. Creating PUT contract...")
        put = Option('SPY', target_exp, atm_strike, 'P', 'SMART')
        contracts = ib.qualifyContracts(put)

        if not contracts:
            print("   [ERROR] Could not qualify contract")
            return

        put = contracts[0]
        print(f"   [OK] Contract: {put.localSymbol}")

        # Create MARKET order
        print(f"\n4. Placing MARKET order...")
        order = MarketOrder('SELL', 1)

        print(f"   SELL 1 {put.localSymbol} MKT")

        trade = ib.placeOrder(put, order)
        ib.sleep(3)

        print(f"\n   Order ID: {trade.order.orderId}")
        print(f"   Status: {trade.orderStatus.status}")

        # Wait a bit and check if filled
        print(f"\n5. Waiting for fill...")
        for i in range(10):
            ib.sleep(1)
            if trade.orderStatus.status == 'Filled':
                print(f"   ✓ FILLED!")
                break
            elif trade.orderStatus.status in ['Cancelled', 'Inactive']:
                print(f"   ✗ Order {trade.orderStatus.status}")
                break
            else:
                print(f"   Status: {trade.orderStatus.status} (waiting...)")

        # Check positions
        print(f"\n6. Checking positions...")
        positions = ib.positions()

        if positions:
            print(f"\n   YOUR POSITIONS:")
            for pos in positions:
                symbol = pos.contract.localSymbol if hasattr(pos.contract, 'localSymbol') else pos.contract.symbol
                print(f"   ✓ {symbol}: {pos.position} contracts @ ${pos.avgCost:.2f}")
        else:
            print(f"   No positions yet (may take a moment in paper trading)")

        print("\n" + "=" * 70)
        print("DONE!")
        print("=" * 70)
        print("\nCheck TWS Portfolio window for your position.")
        print("If still not filled, paper trading may have connectivity issues.")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

    finally:
        ib.disconnect()

if __name__ == "__main__":
    main()
