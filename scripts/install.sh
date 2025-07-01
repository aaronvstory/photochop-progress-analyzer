#!/bin/bash
# Install script for Unix-like systems (macOS, Linux)

echo "=================================================="
echo "Photochop Progress Analyzer - Installation Script"
echo "=================================================="
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ and try again"
    echo "Visit: https://python.org/downloads"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Found Python $PYTHON_VERSION"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed"
    echo "Please install pip and try again"
    exit 1
fi

echo "✅ Found pip3"

# Install dependencies
echo
echo "📦 Installing dependencies..."
pip3 install psutil

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    echo "Try running: pip3 install --user psutil"
    exit 1
fi

# Make scripts executable
echo
echo "🔧 Setting up permissions..."
chmod +x ../src/photoshop_monitor.py
chmod +x install.sh

echo "✅ Permissions set"

# Test installation
echo
echo "🧪 Testing installation..."
cd ../src/
python3 photoshop_monitor.py --help > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Installation test passed"
else
    echo "❌ Installation test failed"
    echo "Please check the setup manually"
    exit 1
fi

echo
echo "=================================================="
echo "🎉 Installation completed successfully!"
echo "=================================================="
echo
echo "Quick start:"
echo "  cd ../src/"
echo "  python3 photoshop_monitor.py --select-folder"
echo
echo "For detailed usage instructions, see:"
echo "  ../docs/SETUP.md"
echo "  ../README.md"
echo
