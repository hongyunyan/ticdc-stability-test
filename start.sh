#!/bin/bash

# TiCDC Stability Test Startup Script

set -e

echo "=========================================="
echo "TiCDC Stability Test - Startup Script"
echo "=========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

# Check if config.env exists
if [ ! -f "config.env" ]; then
    echo "❌ config.env file not found. Please create it first."
    echo "You can copy from the template and update with your GitHub credentials."
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Test configuration
echo "🔧 Testing configuration..."
python3 test_config.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup completed successfully!"
    echo ""
    echo "Usage:"
    echo "  python3 scheduler.py run-now  - Run test immediately"
    echo "  python3 scheduler.py schedule - Start daily scheduler"
    echo ""
    echo "For server deployment, see README.md for systemd or cron setup."
else
    echo ""
    echo "❌ Configuration test failed. Please check your config.env file."
    exit 1
fi
