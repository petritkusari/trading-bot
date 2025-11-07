"""
Buy 100 AAPL shares - Paper Trading
"""
from ib_connection import connect_ib
from ib_insync import Stock, MarketOrder

def main():
    print("=" * 70)
    print("BUYING 100 AAPL SHARES")
    print("=" * 70)

    # Connect to TWS or IB Gateway (whichever is running)
    ib, connection_info = connect_ib(client_id=1)
    print(f"\nConnected to: {connection_info}")

    try:
        # Create AAPL stock contract
        print("\n1. Creating AAPL stock contract...")
        aapl = Stock('AAPL', 'SMART', 'USD')
        ib.qualifyContracts(aapl)
        print(f"   [OK] Contract: {aapl.symbol} ({aapl.primaryExchange})")

        # Get current price
        print("\n2. Getting current AAPL price...")
        ib.reqMarketDataType(3)  # Delayed data for paper trading
        ticker = ib.reqMktData(aapl, '', False, False)
        ib.sleep(2)

        current_price = None
        if ticker.last and ticker.last > 0:
            current_price = ticker.last
        elif ticker.close and ticker.close > 0:
            current_price = ticker.close
        elif ticker.bid and ticker.bid > 0:
            current_price = ticker.bid
        else:
            current_price = 269.0  # Estimate if no data

        print(f"   AAPL Price: ${current_price:.2f}")
        print(f"   Order Value: ${current_price * 100:,.2f}")

        # Create BUY order for 100 shares
        print("\n3. Creating BUY order...")
        print(f"   BUY 100 AAPL @ MARKET")

        order = MarketOrder(
            action='BUY',
            totalQuantity=100
        )

        # Place the order
        print("\n4. Placing order...")
        trade = ib.placeOrder(aapl, order)

        # Wait for order to be submitted
        ib.sleep(3)

        print(f"\n   [OK] Order placed!")
        print(f"   Order ID: {trade.order.orderId}")
        print(f"   Status: {trade.orderStatus.status}")

        # Wait a bit more and check status
        print("\n5. Waiting for fill...")
        for i in range(10):
            ib.sleep(1)
            status = trade.orderStatus.status
            filled = trade.orderStatus.filled
            remaining = trade.orderStatus.remaining

            print(f"   Status: {status} | Filled: {filled} | Remaining: {remaining}")

            if status == 'Filled':
                print(f"\n   [OK] ORDER FILLED!")
                break
            elif status in ['Cancelled', 'Inactive', 'ApiCancelled']:
                print(f"\n   [!] Order {status}")
                break

        # Check final position
        print("\n6. Checking your AAPL position...")
        positions = [p for p in ib.positions() if p.contract.symbol == 'AAPL']

        if positions:
            for pos in positions:
                if pos.contract.secType == 'STK':  # Stock only
                    print(f"\n   AAPL Stock Position:")
                    print(f"   Quantity: {pos.position}")
                    print(f"   Avg Cost: ${pos.avgCost:.2f}")
                    print(f"   Market Value: ${pos.marketValue:,.2f}")
        else:
            print("   Position not showing yet (may take a moment)")

        print("\n" + "=" * 70)
        print("ORDER COMPLETE!")
        print("=" * 70)
        print("\nCheck your TWS Account window to see the updated position.")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

    finally:
        ib.disconnect()
        print("\nDisconnected from TWS")

if __name__ == "__main__":
    main()
