"""
Example: Using the Smart Connection Helper
This script works with BOTH IB Gateway and TWS automatically!
"""
from ib_connection import connect_ib

def main():
    print("=" * 60)
    print("SMART CONNECTION EXAMPLE")
    print("=" * 60)
    print("\nThis will connect to whichever is running:")
    print("  - IB Gateway (port 4002)")
    print("  - TWS (port 7497)")
    print()

    # Connect automatically to whichever is running
    ib, connection_info = connect_ib(client_id=1)

    print(f"\nConnected to: {connection_info}")

    # Now use 'ib' just like before
    print("\nFetching account info...")
    accounts = ib.managedAccounts()
    print(f"Accounts: {accounts}")

    # Get portfolio
    print("\nFetching portfolio positions...")
    portfolio = ib.portfolio()

    if portfolio:
        print(f"\nYou have {len(portfolio)} position(s):")
        for pos in portfolio[:5]:  # Show first 5
            symbol = pos.contract.symbol
            position = pos.position
            value = pos.marketValue
            print(f"  {symbol}: {position} @ ${value:,.2f}")
    else:
        print("No positions")

    # Disconnect
    ib.disconnect()
    print("\nDisconnected successfully!")
    print("\n" + "=" * 60)
    print("DONE! You can now switch between Gateway and TWS anytime.")
    print("=" * 60)

if __name__ == "__main__":
    main()
