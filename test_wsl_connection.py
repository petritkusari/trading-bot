#!/usr/bin/env python3
"""
Test IB Gateway connection from WSL to Windows
"""
from ib_insync import IB
import socket

print("=" * 60)
print("WSL to Windows IB Gateway Connection Test")
print("=" * 60)

# Method 1: Try to get Windows IP from WSL
print("\n1. Finding Windows host IP...")
try:
    with open('/etc/resolv.conf', 'r') as f:
        for line in f:
            if 'nameserver' in line:
                windows_ip = line.split()[1]
                print(f"   Found Windows IP: {windows_ip}")
                break
except:
    windows_ip = None
    print("   Could not find Windows IP from /etc/resolv.conf")

# Test ports
hosts_to_test = []
if windows_ip:
    hosts_to_test.append((windows_ip, 4002, "Windows IP, port 4002 (Gateway Paper)"))
    hosts_to_test.append((windows_ip, 7497, "Windows IP, port 7497 (TWS Paper)"))

hosts_to_test.append(("127.0.0.1", 4002, "localhost, port 4002"))
hosts_to_test.append(("127.0.0.1", 7497, "localhost, port 7497"))

print("\n2. Testing connections...")
print("-" * 60)

for host, port, description in hosts_to_test:
    print(f"\n   Testing {description}")
    print(f"   → {host}:{port}...", end=" ")
    
    ib = IB()
    try:
        ib.connect(host, port, clientId=99, timeout=3)
        print(f"✅ SUCCESS!")
        accounts = ib.managedAccounts()
        print(f"      Accounts: {accounts}")
        ib.disconnect()
        
        print("\n" + "=" * 60)
        print(f"🎉 FOUND IT! IB Gateway is at: {host}:{port}")
        print("=" * 60)
        print(f"\nUpdate ib_config.py:")
        print(f"   IB_HOST = '{host}'")
        print(f"   IB_PORT = {port}")
        break
    except Exception as e:
        print(f"❌ Failed")
        ib.disconnect()
else:
    print("\n" + "=" * 60)
    print("❌ Could not connect to IB Gateway")
    print("=" * 60)
    print("\nPossible issues:")
    print("1. IB Gateway is not running")
    print("2. API is not enabled in Gateway settings")
    print("3. Windows Firewall is blocking the connection")
    print("\nNext steps:")
    print("1. Check IB Gateway is open and logged in")
    print("2. In Gateway: Configure → API → Settings")
    print("   - Look for 'Enable API' checkbox")
    print("   - Make sure it's CHECKED")
    print("3. Check Windows Firewall settings")
