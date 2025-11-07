from ib_insync import IB

print("Testing IB Gateway connection to Windows...")
print("=" * 60)

# Test the Windows host IP
windows_ip = "21.0.0.1"
port = 4002

print(f"\nTrying {windows_ip}:{port}...")

ib = IB()
try:
    ib.connect(windows_ip, port, clientId=99, timeout=5)
    print("✅ SUCCESS!")
    print(f"\n🎉 Connected to IB Gateway!")
    
    accounts = ib.managedAccounts()
    print(f"Accounts: {accounts}")
    
    # Get some account info
    summary = ib.accountSummary()
    for item in summary[:5]:
        print(f"{item.tag}: {item.value}")
    
    ib.disconnect()
    
    print("\n" + "=" * 60)
    print("CONNECTION SUCCESSFUL!")
    print("=" * 60)
    print(f"\nUpdate your ib_config.py:")
    print(f"  IB_HOST = '{windows_ip}'")
    print(f"  IB_PORT = {port}")
    
except Exception as e:
    print(f"❌ Failed: {e}")
    ib.disconnect()
    print("\nMake sure:")
    print("1. IB Gateway is running and logged in")
    print("2. You restarted Gateway after unchecking Read-Only API")
    print("3. Gateway shows 'Connected' status")
