"""
Check option positions and close In-The-Money (ITM) options
"""
from ib_connection import connect_ib
from ib_insync import Stock, MarketOrder

def main():
    print("=" * 70)
    print("CHECKING OPTIONS AND CLOSING ITM POSITIONS")
    print("=" * 70)

    # Connect to TWS or IB Gateway
    ib, connection_info = connect_ib(client_id=1)
    print(f"\nConnected to: {connection_info}")

    try:
        # Get all positions
        print("\n1. Fetching all positions...")
        positions = ib.positions()

        # Filter for options only
        option_positions = [p for p in positions if p.contract.secType == 'OPT']

        if not option_positions:
            print("   No option positions found.")
            return

        print(f"   Found {len(option_positions)} option position(s)")

        # Check each option
        print("\n2. Analyzing option positions...")
        print("=" * 70)

        positions_to_close = []

        for pos in option_positions:
            contract = pos.contract
            position_size = pos.position
            avg_cost = pos.avgCost

            print(f"\n   Option: {contract.localSymbol}")
            print(f"   Symbol: {contract.symbol}")
            print(f"   Strike: ${contract.strike}")
            print(f"   Type: {contract.right} (PUT/CALL)")
            print(f"   Expiry: {contract.lastTradeDateOrContractMonth}")
            print(f"   Position: {position_size} contracts")
            print(f"   Avg Cost: ${avg_cost:.2f}")

            # Get underlying stock price
            print(f"   Fetching {contract.symbol} current price...")
            stock = Stock(contract.symbol, 'SMART', 'USD')
            ib.qualifyContracts(stock)

            ib.reqMarketDataType(3)  # Delayed data
            ticker = ib.reqMktData(stock, '', False, False)
            ib.sleep(2)

            current_price = None
            if ticker.last and ticker.last > 0:
                current_price = ticker.last
            elif ticker.close and ticker.close > 0:
                current_price = ticker.close
            elif ticker.bid and ticker.bid > 0:
                current_price = ticker.bid

            if not current_price:
                print(f"   WARNING: Could not get price for {contract.symbol}")
                continue

            print(f"   {contract.symbol} Current Price: ${current_price:.2f}")

            # Determine if ITM
            is_itm = False
            itm_amount = 0

            if contract.right == 'C':  # CALL option
                if current_price > contract.strike:
                    is_itm = True
                    itm_amount = current_price - contract.strike
                    print(f"   STATUS: IN THE MONEY by ${itm_amount:.2f}")
                else:
                    print(f"   STATUS: Out of the money by ${contract.strike - current_price:.2f}")
            elif contract.right == 'P':  # PUT option
                if current_price < contract.strike:
                    is_itm = True
                    itm_amount = contract.strike - current_price
                    print(f"   STATUS: IN THE MONEY by ${itm_amount:.2f}")
                else:
                    print(f"   STATUS: Out of the money by ${current_price - contract.strike:.2f}")

            # Determine action needed to close
            if is_itm:
                if position_size < 0:  # Short position (sold)
                    action = "BUY"  # Buy to close
                    print(f"   ACTION: Will {action} to close short position")
                else:  # Long position (bought)
                    action = "SELL"  # Sell to close
                    print(f"   ACTION: Will {action} to close long position")

                positions_to_close.append({
                    'contract': contract,
                    'position': position_size,
                    'action': action,
                    'quantity': abs(position_size)
                })

        # Close ITM positions
        if not positions_to_close:
            print("\n" + "=" * 70)
            print("NO ITM POSITIONS TO CLOSE")
            print("=" * 70)
            print("\nAll your options are out of the money. Nothing to close.")
            return

        print("\n" + "=" * 70)
        print(f"FOUND {len(positions_to_close)} ITM POSITION(S) TO CLOSE")
        print("=" * 70)

        for i, pos_info in enumerate(positions_to_close, 1):
            print(f"\n3.{i} Closing position: {pos_info['contract'].localSymbol}")
            print(f"    Action: {pos_info['action']} {pos_info['quantity']} contract(s)")

            # Qualify the contract to get full details
            contract = pos_info['contract']
            contract.exchange = 'SMART'
            ib.qualifyContracts(contract)

            # Create order
            order = MarketOrder(
                action=pos_info['action'],
                totalQuantity=pos_info['quantity']
            )

            # Place order
            print(f"    Placing order...")
            trade = ib.placeOrder(contract, order)
            ib.sleep(3)

            print(f"    Order ID: {trade.order.orderId}")
            print(f"    Status: {trade.orderStatus.status}")

            # Wait for fill
            for j in range(10):
                ib.sleep(1)
                status = trade.orderStatus.status
                filled = trade.orderStatus.filled

                if status == 'Filled':
                    print(f"    [OK] Position closed! Filled: {filled}")
                    break
                elif status in ['Cancelled', 'Inactive', 'ApiCancelled']:
                    print(f"    [!] Order {status}")
                    break

        print("\n" + "=" * 70)
        print("ALL ITM OPTIONS CLOSED!")
        print("=" * 70)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

    finally:
        ib.disconnect()
        print("\nDisconnected")

if __name__ == "__main__":
    main()
