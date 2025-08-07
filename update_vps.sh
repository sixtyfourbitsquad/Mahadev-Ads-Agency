#!/bin/bash

# VPS Update Script for Telegram Bot
# This script updates the bot files from GitHub

set -e

echo "🔄 Updating Telegram Bot on VPS"
echo "================================"

# Configuration
BOT_DIR="/home/bot/telegram-bots/ram-tg-bot"
SERVICE_NAME="telegram-bot-ram"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as bot user
if [ "$USER" != "bot" ]; then
    print_error "This script should be run as bot user"
    print_warning "Run: sudo su - bot"
    exit 1
fi

# Check if bot directory exists
if [ ! -d "$BOT_DIR" ]; then
    print_error "Bot directory not found: $BOT_DIR"
    print_warning "Please run deploy_bot_user.sh first"
    exit 1
fi

# Navigate to bot directory
cd "$BOT_DIR"

print_status "Stopping bot service..."
sudo systemctl stop $SERVICE_NAME

print_status "Backing up current files..."
cp -r . ../ram-tg-bot-backup-$(date +%Y%m%d_%H%M%S)

print_status "Pulling latest changes from GitHub..."
git fetch origin
git reset --hard origin/main

print_status "Updating dependencies..."
source venv/bin/activate
pip install -r requirements.txt

print_status "Starting bot service..."
sudo systemctl start $SERVICE_NAME

print_status "Checking service status..."
sleep 3
sudo systemctl status $SERVICE_NAME --no-pager

print_status "✅ Bot updated successfully!"
print_status "📋 New features available:"
echo "   • Multiple admin support"
echo "   • Simplified admin panel"
echo "   • Channel selection workflow"
echo "   • Admin management script"

print_status "🔧 To manage admins, run:"
echo "   python3 manage_admins.py"
