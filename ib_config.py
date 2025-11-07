"""
Interactive Brokers Connection Configuration
Centralized config for switching between TWS and IB Gateway
"""

# CONNECTION SETTINGS
# ====================

# Choose your connection type:
USE_IB_GATEWAY = True  # Set to True for IB Gateway, False for TWS

# Connection parameters
if USE_IB_GATEWAY:
    # IB Gateway settings
    IB_HOST = '127.0.0.1'
    IB_PORT = 4002  # Paper trading (use 4001 for live)
    CONNECTION_TYPE = "IB Gateway (Paper Trading)"
else:
    # TWS settings
    IB_HOST = '127.0.0.1'
    IB_PORT = 7497  # Paper trading (use 7496 for live)
    CONNECTION_TYPE = "TWS (Paper Trading)"

# Client IDs for different scripts (each script needs unique ID)
CLIENT_IDS = {
    'tws_connect_test': 1,
    'place_vxx_put': 2,
    'place_spy_put': 3,
    'check_orders': 4,
    'cancel_orders': 5,
    'check_vxx_options': 6,
    'find_contracts': 7,
    'weekly_tracker': 8,
    'real_tracker': 9,
}

# Timeout settings
CONNECTION_TIMEOUT = 10  # seconds
REQUEST_TIMEOUT = 30  # seconds

def get_connection_params(script_name='default'):
    """
    Get connection parameters for a script

    Args:
        script_name: Name of the script (e.g., 'place_vxx_put')

    Returns:
        dict: Connection parameters (host, port, clientId)
    """
    client_id = CLIENT_IDS.get(script_name, 10)  # Default to 10 if not found

    return {
        'host': IB_HOST,
        'port': IB_PORT,
        'clientId': client_id,
        'connection_type': CONNECTION_TYPE
    }

def print_connection_info(script_name='default'):
    """Print connection information"""
    params = get_connection_params(script_name)
    print("=" * 60)
    print(f"CONNECTION: {params['connection_type']}")
    print(f"Host: {params['host']}:{params['port']}")
    print(f"Client ID: {params['clientId']}")
    print("=" * 60)

if __name__ == "__main__":
    # Test the config
    print("\nCurrent Configuration:")
    print_connection_info()
    print(f"\nUse IB Gateway: {USE_IB_GATEWAY}")
    print(f"Port: {IB_PORT}")
    print(f"\nTo switch:")
    print("  - For IB Gateway: Set USE_IB_GATEWAY = True")
    print("  - For TWS: Set USE_IB_GATEWAY = False")
