"""
Test IB API Connection and Check Current Positions/Orders
Works with both TWS and IB Gateway - configure in ib_config.py
"""
from ib_insync import *
import sys
from ib_config import get_connection_params, print_connection_info

def main():
    # Get connection parameters from config
    params = get_connection_params('tws_connect_test')

    print_connection_info('tws_connect_test')

    # Create IB connection
    ib = IB()

    try:
        # Connect using configured parameters
        print(f"\n1. Attempting connection to {params['host']}:{params['port']}...")
        ib.connect(params['host'], params['port'], clientId=params['clientId'])
        print("[OK] CONNECTED SUCCESSFULLY!")

        # Get account info
        print("\n2. Checking account information...")
        accounts = ib.managedAccounts()
        print(f"   Accounts: {accounts}")

        # Get portfolio positions
        print("\n3. Current Portfolio Positions:")
        print("-" * 60)
        portfolio = ib.portfolio()
        if portfolio:
            for position in portfolio:
                print(f"\n   Symbol: {position.contract.symbol}")
                print(f"   Position: {position.position}")
                print(f"   Market Value: ${position.marketValue:,.2f}")
                print(f"   Avg Cost: ${position.averageCost:.2f}")
                print(f"   Unrealized P&L: ${position.unrealizedPNL:,.2f}")
        else:
            print("   No open positions")

        # Get open orders (trades)
        print("\n4. Current Open Orders:")
        print("-" * 60)
        trades = ib.openTrades()
        if trades:
            for trade in trades:
                print(f"\n   Symbol: {trade.contract.symbol}")
                print(f"   Action: {trade.order.action}")
                print(f"   Quantity: {trade.order.totalQuantity}")
                print(f"   Order Type: {trade.order.orderType}")
                print(f"   Status: {trade.orderStatus.status}")
                if hasattr(trade.contract, 'right'):
                    print(f"   Option Type: {trade.contract.right}")
                    print(f"   Strike: ${trade.contract.strike}")
                    print(f"   Expiry: {trade.contract.lastTradeDateOrContractMonth}")
        else:
            print("   No open orders")

        # Get account summary
        print("\n5. Account Summary:")
        print("-" * 60)
        account_values = ib.accountSummary()
        important_values = ['NetLiquidation', 'TotalCashValue', 'BuyingPower', 'UnrealizedPnL']
        for value in account_values:
            if value.tag in important_values:
                print(f"   {value.tag}: ${float(value.value):,.2f}")

        print("\n" + "=" * 60)
        print("CONNECTION TEST SUCCESSFUL!")
        print("=" * 60)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nTroubleshooting:")
        print(f"1. Is {params['connection_type']} running?")
        print("2. Is 'Enable ActiveX and Socket Clients' checked?")
        print("3. Is 'Read-Only API' UNCHECKED?")
        print("4. Did you click OK and restart if prompted?")
        print(f"5. Check ib_config.py - current port: {params['port']}")
        sys.exit(1)

    finally:
        ib.disconnect()
        print(f"\nDisconnected from {params['connection_type']}")

if __name__ == "__main__":
    main()
