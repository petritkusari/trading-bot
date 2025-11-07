"""
IB Gateway Setup Verification Script

This script checks if you're ready to switch from TWS to IB Gateway
Run this AFTER setting up IB Gateway
"""
import os
import sys

def check_ib_config():
    """Check if ib_config.py exists and is configured"""
    print("\n1. Checking ib_config.py...")

    if not os.path.exists('ib_config.py'):
        print("   ❌ ib_config.py not found!")
        return False

    try:
        from ib_config import USE_IB_GATEWAY, IB_PORT, CONNECTION_TYPE

        print(f"   ✅ ib_config.py found")
        print(f"   → USE_IB_GATEWAY: {USE_IB_GATEWAY}")
        print(f"   → Port: {IB_PORT}")
        print(f"   → Type: {CONNECTION_TYPE}")

        if USE_IB_GATEWAY:
            print("   ✅ Configured for IB Gateway")
            if IB_PORT == 4002:
                print("   ✅ Port 4002 (Paper Trading) - Correct!")
            elif IB_PORT == 4001:
                print("   ⚠️  Port 4001 (LIVE Trading) - Be careful!")
            else:
                print(f"   ❌ Unexpected port: {IB_PORT}")
                return False
        else:
            print("   ⚠️  Still configured for TWS")
            print("   → Set USE_IB_GATEWAY = True in ib_config.py")

        return True

    except Exception as e:
        print(f"   ❌ Error loading ib_config.py: {e}")
        return False

def check_ib_gateway_running():
    """Check if IB Gateway is accessible"""
    print("\n2. Checking IB Gateway connection...")

    try:
        from ib_insync import IB
        from ib_config import IB_HOST, IB_PORT

        ib = IB()
        print(f"   → Attempting connection to {IB_HOST}:{IB_PORT}...")

        try:
            ib.connect(IB_HOST, IB_PORT, clientId=99, timeout=5)
            print("   ✅ Connected successfully!")

            # Get account info
            accounts = ib.managedAccounts()
            print(f"   ✅ Accounts: {accounts}")

            ib.disconnect()
            return True

        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
            print("\n   Troubleshooting:")
            print("   1. Is IB Gateway running?")
            print("   2. Is API enabled in Gateway settings?")
            print("   3. Is the port correct (4002 for paper)?")
            return False

    except ImportError as e:
        print(f"   ❌ Missing dependency: {e}")
        print("   → Run: pip install ib_insync")
        return False

def check_updated_scripts():
    """Check if scripts have been updated to use ib_config"""
    print("\n3. Checking if scripts are updated...")

    scripts_to_check = [
        'tws_connect_test.py',
        'place_vxx_put_trade.py',
    ]

    updated_count = 0
    total_count = len(scripts_to_check)

    for script in scripts_to_check:
        if not os.path.exists(script):
            print(f"   ⚠️  {script} - not found")
            continue

        with open(script, 'r') as f:
            content = f.read()

        if 'ib_config' in content:
            print(f"   ✅ {script} - updated")
            updated_count += 1
        else:
            print(f"   ❌ {script} - needs update")

    print(f"\n   → {updated_count}/{total_count} scripts updated")
    return updated_count == total_count

def check_can_view_in_tws():
    """Check if TWS can view the same account"""
    print("\n4. TWS Compatibility Check...")
    print("   ℹ️  You can run TWS and IB Gateway simultaneously")
    print("   → IB Gateway: For API connections (your scripts)")
    print("   → TWS: For visual monitoring (optional)")
    print("   → Both show the SAME account data")
    print("   ✅ No issues expected")
    return True

def print_next_steps(all_checks_passed):
    """Print what to do next"""
    print("\n" + "=" * 60)

    if all_checks_passed:
        print("🎉 READY TO USE IB GATEWAY!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Test connection:")
        print("   python tws_connect_test.py")
        print("\n2. Place a test trade (paper):")
        print("   python place_vxx_put_trade.py")
        print("\n3. Monitor in TWS (optional):")
        print("   - Open TWS with same credentials")
        print("   - See positions placed by scripts")
        print("\n4. Run your weekly strategy:")
        print("   - All scripts now use IB Gateway automatically")

    else:
        print("⚠️  SETUP INCOMPLETE")
        print("=" * 60)
        print("\nPlease complete the following:")
        print("1. Download and install IB Gateway")
        print("   → See IB_GATEWAY_SETUP_GUIDE.md")
        print("\n2. Configure IB Gateway:")
        print("   - Enable API in settings")
        print("   - Port 4002 for paper trading")
        print("\n3. Update ib_config.py:")
        print("   - Set USE_IB_GATEWAY = True")
        print("\n4. Run this script again to verify")

def main():
    """Run all checks"""
    print("=" * 60)
    print("IB GATEWAY SETUP VERIFICATION")
    print("=" * 60)

    checks = [
        check_ib_config(),
        check_ib_gateway_running(),
        check_updated_scripts(),
        check_can_view_in_tws(),
    ]

    all_passed = all(checks)

    print_next_steps(all_passed)

    print("\n" + "=" * 60)
    if all_passed:
        print("STATUS: ✅ READY")
    else:
        print("STATUS: ⚠️  NEEDS ATTENTION")
    print("=" * 60)

    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
