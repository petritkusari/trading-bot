from ib_insync import IB
import sys

ports_to_try = [4002, 7497, 4001, 7496]

print("Testing different ports...")
print("=" * 60)

for port in ports_to_try:
    print(f"\nTrying port {port}...", end=" ")
    ib = IB()
    try:
        ib.connect('127.0.0.1', port, clientId=99, timeout=3)
        print(f"✅ SUCCESS!")
        print(f"   Connected to port {port}")
        accounts = ib.managedAccounts()
        print(f"   Accounts: {accounts}")
        ib.disconnect()
        print(f"\n🎉 IB Gateway is listening on port {port}")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Failed")
        ib.disconnect()

print("\n" + "=" * 60)
print("❌ Could not connect to any port")
print("\nPlease check:")
print("1. Is IB Gateway actually running?")
print("2. Check the API settings in Gateway")
