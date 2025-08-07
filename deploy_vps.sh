#!/bin/bash

# Telegram Bot VPS Deployment Script
# This script helps deploy the bot alongside existing bots

set -e

echo "🚀 Telegram Bot VPS Deployment Script"
echo "======================================"

# Configuration
BOT_NAME="ram-tg-bot"
BOT_DIR="/opt/telegram-bots/$BOT_NAME"
SERVICE_NAME="telegram-bot-ram"
PYTHON_VERSION="python3"

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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Check if bot directory exists
if [ -d "$BOT_DIR" ]; then
    print_warning "Bot directory already exists at $BOT_DIR"
    read -p "Do you want to backup and overwrite? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Creating backup..."
        sudo cp -r "$BOT_DIR" "${BOT_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
    else
        print_error "Deployment cancelled"
        exit 1
    fi
fi

# Create bot directory
print_status "Creating bot directory..."
sudo mkdir -p "$BOT_DIR"
sudo chown $USER:$USER "$BOT_DIR"

# Copy bot files
print_status "Copying bot files..."
cp -r . "$BOT_DIR/"
cd "$BOT_DIR"

# Create virtual environment
print_status "Setting up Python virtual environment..."
$PYTHON_VERSION -m venv venv
source venv/bin/activate

# Install dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service file
print_status "Creating systemd service..."
sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null <<EOF
[Unit]
Description=Telegram Auto-Join Bot (Ram)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$BOT_DIR
Environment=PATH=$BOT_DIR/venv/bin
ExecStart=$BOT_DIR/venv/bin/python bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
print_status "Reloading systemd..."
sudo systemctl daemon-reload

# Enable service
print_status "Enabling service..."
sudo systemctl enable $SERVICE_NAME

print_status "Deployment completed!"
echo
echo "📋 Next steps:"
echo "1. Set your bot token in $BOT_DIR/.env"
echo "2. Add your admin ID to $BOT_DIR/admins.json"
echo "3. Start the service: sudo systemctl start $SERVICE_NAME"
echo "4. Check status: sudo systemctl status $SERVICE_NAME"
echo "5. View logs: sudo journalctl -u $SERVICE_NAME -f"
echo
echo "🔧 Service management:"
echo "   Start:   sudo systemctl start $SERVICE_NAME"
echo "   Stop:    sudo systemctl stop $SERVICE_NAME"
echo "   Restart: sudo systemctl restart $SERVICE_NAME"
echo "   Status:  sudo systemctl status $SERVICE_NAME"
echo "   Logs:    sudo journalctl -u $SERVICE_NAME -f"
echo
echo "📁 Bot directory: $BOT_DIR"
echo "🔗 Service name: $SERVICE_NAME"
