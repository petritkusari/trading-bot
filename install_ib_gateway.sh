#!/bin/bash
# IB Gateway Installer for Linux

echo "============================================================"
echo "IB GATEWAY INSTALLATION SCRIPT"
echo "============================================================"
echo ""
echo "This script will download and install IB Gateway"
echo ""

# Download URL
DOWNLOAD_URL="https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-linux-x64.sh"
INSTALLER_FILE="ibgateway-installer.sh"

echo "Step 1: Downloading IB Gateway..."
echo "URL: $DOWNLOAD_URL"
echo ""

# Download the installer
wget -O "$INSTALLER_FILE" "$DOWNLOAD_URL"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Download failed!"
    echo ""
    echo "Please download manually from:"
    echo "https://www.interactivebrokers.com/en/trading/ibgateway-stable.php"
    exit 1
fi

echo ""
echo "✅ Download complete!"
echo ""
echo "Step 2: Making installer executable..."
chmod +x "$INSTALLER_FILE"

echo ""
echo "✅ Ready to install!"
echo ""
echo "============================================================"
echo "NEXT STEPS:"
echo "============================================================"
echo ""
echo "1. Run the installer:"
echo "   ./$INSTALLER_FILE"
echo ""
echo "2. Follow the installation wizard"
echo "3. Choose installation directory (default is fine)"
echo "4. Wait for installation to complete"
echo ""
echo "After installation:"
echo "5. Launch IB Gateway"
echo "6. Configure API settings (I'll help you with this)"
echo ""
echo "Ready to run the installer? (The installer will open a GUI)"
echo ""
read -p "Run installer now? (y/n): " response

if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    echo ""
    echo "Launching installer..."
    ./"$INSTALLER_FILE"
else
    echo ""
    echo "Installer ready at: ./$INSTALLER_FILE"
    echo "Run it when you're ready: ./$INSTALLER_FILE"
fi
