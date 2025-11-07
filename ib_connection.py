"""
Smart IB Connection Helper
Automatically connects to either IB Gateway or TWS - whichever is running
"""
from ib_insync import IB

def connect_ib(client_id=1):
    """
    Tries to connect to IB Gateway first (port 4002), then TWS (port 7497)
    Returns: (ib, connection_info) tuple
    """
    ib = IB()

    # Try IB Gateway first (port 4002) - Paper Trading
    try:
        print("Attempting to connect to IB Gateway (port 4002)...")
        ib.connect('127.0.0.1', 4002, clientId=client_id)
        print("[OK] Connected to IB Gateway (port 4002)")
        return ib, "IB Gateway - Port 4002"
    except Exception as e:
        print(f"IB Gateway not available: {e}")

    # Try TWS if Gateway failed (port 7497) - Paper Trading
    try:
        print("Attempting to connect to TWS (port 7497)...")
        ib.connect('127.0.0.1', 7497, clientId=client_id)
        print("[OK] Connected to TWS (port 7497)")
        return ib, "TWS - Port 7497"
    except Exception as e:
        print(f"TWS not available: {e}")

    # Both failed
    raise ConnectionError(
        "Could not connect to IB Gateway or TWS.\n"
        "Please make sure one of them is running with:\n"
        "  - IB Gateway on port 4002 (recommended for bots)\n"
        "  - TWS on port 7497 (for manual trading)\n"
        "\n"
        "Also check that API settings are enabled."
    )

def get_connection_ports():
    """
    Returns the ports for IB Gateway and TWS
    """
    return {
        'gateway': 4002,
        'tws': 7497
    }

if __name__ == "__main__":
    # Test the connection
    print("=" * 60)
    print("TESTING IB CONNECTION")
    print("=" * 60)

    try:
        ib, info = connect_ib()
        print(f"\n[OK] Successfully connected to: {info}")

        # Show account info
        accounts = ib.managedAccounts()
        print(f"[OK] Account(s): {accounts}")

        ib.disconnect()
        print("\n[OK] Test successful! You can now use this in your scripts.")
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")
