#!/bin/bash

# Telegram Auto-Join Bot Deployment Script
# This script helps deploy the bot on various platforms

set -e

echo "🤖 Telegram Auto-Join Bot Deployment"
echo "====================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python version $PYTHON_VERSION is too old. Please install Python 3.10 or higher."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Please run: python setup.py"
    echo "Or create .env file manually with your bot token:"
    echo "TELEGRAM_BOT_TOKEN=your_token_here"
    exit 1
fi

# Check if admins.json exists and has content
if [ ! -f "admins.json" ] || [ ! -s "admins.json" ]; then
    echo "⚠️  admins.json is empty or missing!"
    echo "Please run: python setup.py"
    echo "Or edit admins.json manually with your Telegram ID"
    exit 1
fi

echo "✅ All checks passed!"
echo ""
echo "🚀 Starting bot..."
echo "Press Ctrl+C to stop the bot"
echo ""

# Run the bot
python bot.py

