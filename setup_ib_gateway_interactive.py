#!/usr/bin/env python3
"""
Interactive IB Gateway Setup Assistant
Guides you through the complete setup process
"""

import os
import sys
import time

def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def print_step(num, text):
    print(f"\n{num}. {text}")

def ask_question(question, options=None):
    print(f"\n{question}")
    if options:
        for i, opt in enumerate(options, 1):
            print(f"   {i}. {opt}")
    response = input("\nYour answer: ").strip()
    return response

def main():
    print_header("IB GATEWAY SETUP ASSISTANT")
    print("\nThis will guide you through setting up IB Gateway")
    print("for automated trading with your Python scripts.")

    # Step 1: Detect OS
    print_step(1, "Detecting your environment...")

    os_name = ask_question(
        "What is your desktop operating system?",
        ["Windows", "macOS", "Linux Desktop"]
    )

    # Step 2: Download instructions
    print_step(2, "Download IB Gateway")

    if os_name == "1":  # Windows
        print("\n   Windows detected!")
        print("\n   📥 Download from:")
        print("   https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-windows-x64.exe")
        print("\n   OR visit:")
        print("   https://www.interactivebrokers.com/en/trading/ibgateway-stable.php")
        print("\n   Installation steps:")
        print("   1. Run the downloaded .exe file")
        print("   2. Click 'Next' through the wizard")
        print("   3. Accept license agreement")
        print("   4. Use default installation directory")
        print("   5. Click 'Install'")
        print("   6. Wait for completion")
        print("   7. Click 'Finish'")

    elif os_name == "2":  # macOS
        print("\n   macOS detected!")
        print("\n   📥 Download from:")
        print("   https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-macos-x64.dmg")
        print("\n   Installation steps:")
        print("   1. Open the downloaded .dmg file")
        print("   2. Drag IB Gateway to Applications folder")
        print("   3. Go to Applications → IB Gateway")
        print("   4. Right-click → Open (first time only)")
        print("   5. Click 'Open' when warned about developer")

    else:  # Linux
        print("\n   Linux detected!")
        print("\n   📥 Installation:")
        print("   Run this command:")
        print("   ./install_ib_gateway.sh")
        print("\n   Or manually:")
        print("   wget https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-linux-x64.sh")
        print("   chmod +x ibgateway-stable-standalone-linux-x64.sh")
        print("   ./ibgateway-stable-standalone-linux-x64.sh")

    input("\n   Press ENTER when you've downloaded and installed IB Gateway...")

    # Step 3: Launch and login
    print_step(3, "Launch IB Gateway and Login")
    print("\n   1. Launch IB Gateway application")
    print("   2. You should see a login window")
    print("   3. Enter your credentials:")
    print("      - Username: Your paper trading username")
    print("      - Password: Your paper trading password")
    print("      - Trading Mode: Paper Trading (IMPORTANT!)")
    print("   4. Click 'Login'")

    input("\n   Press ENTER when you're logged in and see the Gateway window...")

    # Step 4: Configure API
    print_step(4, "Configure API Settings (CRITICAL!)")
    print("\n   🔧 In the IB Gateway window:")
    print("   1. Click 'Configure' (or gear icon)")
    print("   2. Go to: Settings → API → Settings")
    print("   3. Make these changes:")
    print("\n      ✅ Enable ActiveX and Socket Clients: CHECKED")
    print("      ❌ Read-Only API: UNCHECKED (very important!)")
    print("      ✅ Download open orders on connection: CHECKED")
    print("      ✅ Allow connections from localhost only: CHECKED")
    print("\n      Socket Port: 4002")
    print("      (Paper Trading uses port 4002)")
    print("\n   4. Click 'OK'")
    print("   5. Gateway will say 'Configuration changes require restart'")
    print("   6. Click 'OK'")
    print("   7. CLOSE IB Gateway completely")
    print("   8. RESTART IB Gateway")
    print("   9. Login again")

    input("\n   Press ENTER when you've restarted Gateway and logged in...")

    # Step 5: Verify ib_config.py
    print_step(5, "Verifying Python configuration...")

    try:
        from ib_config import USE_IB_GATEWAY, IB_PORT, CONNECTION_TYPE

        print(f"\n   Current settings:")
        print(f"   - USE_IB_GATEWAY: {USE_IB_GATEWAY}")
        print(f"   - Port: {IB_PORT}")
        print(f"   - Connection Type: {CONNECTION_TYPE}")

        if USE_IB_GATEWAY and IB_PORT == 4002:
            print("\n   ✅ Configuration looks good!")
        else:
            print("\n   ⚠️  Configuration needs adjustment")
            if not USE_IB_GATEWAY:
                print("   → Edit ib_config.py and set USE_IB_GATEWAY = True")
            if IB_PORT != 4002:
                print(f"   → Port is {IB_PORT}, should be 4002 for paper trading")
            input("\n   Press ENTER after fixing ib_config.py...")
    except ImportError:
        print("\n   ❌ Cannot import ib_config.py")
        print("   Make sure you're in the trading-bot directory")
        sys.exit(1)

    # Step 6: Test connection
    print_step(6, "Testing connection...")
    print("\n   Running connection test...")

    input("\n   Press ENTER to run the test (make sure IB Gateway is running)...")

    print("\n   Executing: python tws_connect_test.py")
    print("   " + "-" * 56)

    os.system("python tws_connect_test.py")

    # Step 7: Success check
    print_header("SETUP COMPLETE!")

    success = ask_question(
        "Did the connection test succeed?",
        ["Yes, connected successfully!", "No, got an error"]
    )

    if success == "1":
        print("\n   🎉 CONGRATULATIONS!")
        print("\n   You're now connected to IB Gateway!")
        print("\n   What you can do now:")
        print("   1. Run trading scripts: python place_vxx_put_trade.py")
        print("   2. Open TWS to monitor: See positions placed by scripts")
        print("   3. Switch anytime: Edit ib_config.py")
        print("\n   Next steps:")
        print("   - Read: USING_BOTH_GATEWAY_AND_TWS.md")
        print("   - Test a trade: python place_vxx_put_trade.py")
        print("   - View in TWS: Open TWS and see the same account")

    else:
        print("\n   📋 TROUBLESHOOTING:")
        print("\n   Common issues:")
        print("   1. IB Gateway not running")
        print("      → Launch IB Gateway and login")
        print("\n   2. API not enabled")
        print("      → Gateway → Configure → Settings → API → Settings")
        print("      → Check 'Enable ActiveX and Socket Clients'")
        print("      → Uncheck 'Read-Only API'")
        print("      → Restart Gateway")
        print("\n   3. Wrong port")
        print("      → Port should be 4002 (paper trading)")
        print("      → Check in Gateway API settings")
        print("      → Check in ib_config.py")
        print("\n   4. Firewall blocking")
        print("      → Allow Python and IB Gateway through firewall")
        print("\n   Run this script again after fixing: ./setup_ib_gateway_interactive.py")
        print("   Or check: IB_GATEWAY_SETUP_GUIDE.md")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
