"""
Utility script to update all trading scripts to use ib_config.py
This updates the hardcoded TWS connections to use centralized config
"""
import os
import re

# Files to update
files_to_update = [
    'place_spy_put_trade.py',
    'check_order_status.py',
    'cancel_and_place_new.py',
    'check_vxx_options.py',
    'find_real_vxx_contracts.py'
]

# Old pattern to find
old_connection = "ib.connect('127.0.0.1', 7497, clientId=1)"

# Replacement pattern template
new_connection_template = "ib.connect(params['host'], params['port'], clientId=params['clientId'])"

# Import statement to add
import_statement = "from ib_config import get_connection_params, print_connection_info"

def update_file(filename):
    """Update a single file to use ib_config"""
    if not os.path.exists(filename):
        print(f"❌ Skipping {filename} - file not found")
        return False

    try:
        # Read the file
        with open(filename, 'r') as f:
            content = f.read()

        # Check if already updated
        if 'ib_config' in content:
            print(f"✅ {filename} - already updated")
            return True

        # Add import statement after existing imports
        if import_statement not in content:
            # Find the last import line
            import_pattern = r'(from ib_insync import \*\n)'
            content = re.sub(import_pattern, r'\1' + import_statement + '\n', content, count=1)

        # Replace the connection line
        content = content.replace(old_connection, new_connection_template)

        # Write back
        with open(filename, 'w') as f:
            f.write(content)

        print(f"✅ {filename} - updated successfully")
        return True

    except Exception as e:
        print(f"❌ {filename} - error: {e}")
        return False

def main():
    print("=" * 60)
    print("UPDATING TRADING SCRIPTS TO USE IB_CONFIG.PY")
    print("=" * 60)
    print()

    success_count = 0
    for filename in files_to_update:
        if update_file(filename):
            success_count += 1

    print()
    print("=" * 60)
    print(f"COMPLETE: {success_count}/{len(files_to_update)} files updated")
    print("=" * 60)
    print()
    print("⚠️  Manual steps still needed:")
    print("1. Review each updated file")
    print("2. Add params = get_connection_params('<script_name>') at the start of main()")
    print("3. Test each script with IB Gateway")

if __name__ == "__main__":
    main()
