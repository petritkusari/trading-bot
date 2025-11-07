"""
Place VXX PUT Trade - Your First Correct Trade!
Works with both TWS and IB Gateway - configure in ib_config.py
"""
from ib_insync import *
from ib_config import get_connection_params, print_connection_info

def place_trade():
    # Get connection parameters
    params = get_connection_params('place_vxx_put')

    print("=" * 60)
    print("PLACING VXX PUT TRADE")
    print("=" * 60)
    print_connection_info('place_vxx_put')

    ib = IB()

    try:
        # Connect
        print(f"\n1. Connecting to {params['connection_type']}...")
        ib.connect(params['host'], params['port'], clientId=params['clientId'])
        print("   [OK] Connected to Paper Trading")

        # Define the PUT contract
        print("\n2. Creating PUT contract...")
        put_contract = Option(
            symbol='VXX',
            lastTradeDateOrContractMonth='20251107',  # Nov 7, 2025
            strike=18.0,
            right='P',  # P = PUT
            exchange='SMART'
        )

        # Qualify the contract (get full details from IB)
        print("   Qualifying contract with IB...")
        ib.qualifyContracts(put_contract)
        print(f"   [OK] Contract qualified: {put_contract.localSymbol}")

        # Create the order - SELL TO OPEN
        print("\n3. Creating SELL TO OPEN order...")
        order = MarketOrder(
            action='SELL',      # SELL (not BUY!)
            totalQuantity=10,   # 10 contracts
            transmit=False      # Don't send yet - preview first
        )

        print(f"\n   Order Details:")
        print(f"   --------------")
        print(f"   Action:    SELL TO OPEN")
        print(f"   Quantity:  10 contracts")
        print(f"   Symbol:    VXX")
        print(f"   Type:      PUT")
        print(f"   Strike:    $18.00")
        print(f"   Expiry:    Nov 7, 2025 (2 days)")
        print(f"   Order Type: MARKET")

        # Show what this means
        print(f"\n   What this does:")
        print(f"   - You SELL 10 VXX $18 PUTs")
        print(f"   - You collect premium upfront")
        print(f"   - Cash secured: $18,000 (10 × $18 × 100)")
        print(f"   - If VXX stays above $18 by Friday: PUTs expire worthless, you keep premium")
        print(f"   - If VXX drops below $18: You buy 1000 VXX shares at $18")

        # Preview the trade
        print("\n4. Previewing trade (not placing yet)...")
        trade = ib.placeOrder(put_contract, order)
        ib.sleep(2)

        print(f"   Order ID: {trade.order.orderId}")
        print(f"   Status: {trade.orderStatus.status}")

        # Ask for confirmation
        print("\n" + "=" * 60)
        print("READY TO PLACE TRADE")
        print("=" * 60)

        response = input("\nDo you want to TRANSMIT this order? (yes/no): ").strip().lower()

        if response == 'yes':
            # Transmit the order
            print("\n5. Transmitting order...")
            order.transmit = True
            ib.placeOrder(put_contract, order)
            ib.sleep(2)

            print(f"\n   [OK] Order transmitted!")
            print(f"   Order ID: {trade.order.orderId}")
            print(f"   Status: {trade.orderStatus.status}")

            # Show position
            print("\n6. Checking your position...")
            ib.sleep(2)
            portfolio = ib.portfolio()

            if portfolio:
                print("\n   Your Positions:")
                for pos in portfolio:
                    print(f"   - {pos.contract.localSymbol}: {pos.position} contracts")
                    print(f"     Market Value: ${pos.marketValue:,.2f}")
                    print(f"     P&L: ${pos.unrealizedPNL:,.2f}")
            else:
                print("   Position pending fill...")

            print("\n" + "=" * 60)
            print("CONGRATULATIONS! FIRST TRADE PLACED!")
            print("=" * 60)
            print("\nNext steps:")
            print("1. Monitor position in TWS/IB Gateway Portfolio window")
            print("2. Position will show as: -10 VXX Nov 7 '25 18 PUT")
            print("3. Wait until Friday for expiration")
            print("4. If VXX > $18 on Friday: PUTs expire, you keep premium")
            print("5. Record this trade in your tracking spreadsheet")

        else:
            print("\n   Order NOT transmitted (cancelled)")
            print("   You can run this script again when ready")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

    finally:
        ib.disconnect()
        print(f"\nDisconnected from {params['connection_type']}")

if __name__ == "__main__":
    place_trade()
