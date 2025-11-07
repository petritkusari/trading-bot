#!/bin/bash
echo "Finding Windows host IP from WSL..."
echo ""

# Method 1: Check resolv.conf
echo "Method 1: /etc/resolv.conf"
if [ -f /etc/resolv.conf ]; then
    WINDOWS_IP=$(cat /etc/resolv.conf | grep nameserver | head -1 | awk '{print $2}')
    if [ ! -z "$WINDOWS_IP" ]; then
        echo "Found: $WINDOWS_IP"
    else
        echo "Not found in resolv.conf"
    fi
fi

# Method 2: Check WSL_INTEROP environment
echo ""
echo "Method 2: hostname command"
HOSTNAME_IP=$(hostname -I | awk '{print $1}')
if [ ! -z "$HOSTNAME_IP" ]; then
    echo "WSL IP: $HOSTNAME_IP"
    # Windows is usually the .1 address in the same subnet
    WINDOWS_IP_GUESS=$(echo $HOSTNAME_IP | awk -F. '{print $1"."$2"."$3".1"}')
    echo "Windows IP likely: $WINDOWS_IP_GUESS"
fi

echo ""
echo "=========================================="
if [ ! -z "$WINDOWS_IP" ]; then
    echo "Windows Host IP: $WINDOWS_IP"
else
    echo "Could not automatically detect Windows IP"
    echo ""
    echo "To find it manually in Windows PowerShell, run:"
    echo "  ipconfig"
    echo "Look for 'vEthernet (WSL)' IP address"
fi
