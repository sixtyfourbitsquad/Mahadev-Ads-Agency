#!/bin/bash

# Colors for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== VipPlay247 Telegram Bot Quick Deployment ===${NC}\n"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Get configuration from user
echo -e "${BLUE}Please provide the following information:${NC}"
read -p "Enter Telegram Bot Token: " BOT_TOKEN
read -p "Enter First Admin ID: " ADMIN1_ID
read -p "Enter Second Admin ID: " ADMIN2_ID

# Validate inputs
if [ -z "$BOT_TOKEN" ] || [ -z "$ADMIN1_ID" ] || [ -z "$ADMIN2_ID" ]; then
    echo -e "${RED}Error: All fields are required${NC}"
    exit 1
fi

echo -e "\n${BLUE}Installing system dependencies...${NC}"
apt-get update
apt-get install -y python3 python3-pip python3-venv git

# Create installation directory
INSTALL_DIR="/opt/vipplay247-bot"
echo -e "\n${BLUE}Creating installation directory...${NC}"
mkdir -p $INSTALL_DIR

# Clone the repository
echo -e "\n${BLUE}Cloning the repository...${NC}"
git clone https://github.com/sixtyfourbitsquad/Mahadev-Ads-Agency.git $INSTALL_DIR
cd $INSTALL_DIR

# Setup Python virtual environment
echo -e "\n${BLUE}Setting up Python virtual environment...${NC}"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure the bot
echo -e "\n${BLUE}Configuring the bot...${NC}"
# Create admins.json
echo "[$ADMIN1_ID, $ADMIN2_ID]" > admins.json

# Copy and configure bot_config.json
cp bot_config.json.example bot_config.json

# Create systemd service
echo -e "\n${BLUE}Creating systemd service...${NC}"
cat > /etc/systemd/system/vipplay247-bot.service << EOL
[Unit]
Description=VipPlay247 Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
Environment="TELEGRAM_BOT_TOKEN=$BOT_TOKEN"
ExecStart=$INSTALL_DIR/venv/bin/python bot_advanced.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# Reload systemd and start the bot
echo -e "\n${BLUE}Starting the bot...${NC}"
systemctl daemon-reload
systemctl enable vipplay247-bot
systemctl start vipplay247-bot

# Check status
sleep 3
if systemctl is-active --quiet vipplay247-bot; then
    echo -e "\n${GREEN}✓ VipPlay247 Bot has been successfully deployed!${NC}"
    echo -e "\n${BLUE}Useful commands:${NC}"
    echo "- Check bot status: systemctl status vipplay247-bot"
    echo "- View logs: journalctl -u vipplay247-bot -f"
    echo "- Restart bot: systemctl restart vipplay247-bot"
else
    echo -e "\n${RED}! Warning: Bot service is not running. Please check logs:${NC}"
    echo "journalctl -u vipplay247-bot -f"
fi