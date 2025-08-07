# 🚀 VPS Deployment Guide

This guide will help you deploy the Telegram Auto-Join Bot on your VPS alongside existing bots.

## 📋 Prerequisites

- VPS with Ubuntu/Debian Linux
- Python 3.8+ installed
- Git installed
- Sudo access
- Existing bot running (optional)

## 🎯 Quick Deployment

### 1. **Clone/Upload to VPS**

```bash
# Option 1: Clone from your repository
git clone <your-repo-url> /opt/telegram-bots/ram-tg-bot
cd /opt/telegram-bots/ram-tg-bot

# Option 2: Upload files manually
# Upload all files to /opt/telegram-bots/ram-tg-bot/
```

### 2. **Run Setup Script**

```bash
python3 setup_vps.py
```

This will:
- Create `.env` file with your bot token
- Set up `admins.json` with your user ID
- Create default configuration files

### 3. **Deploy with Script**

```bash
chmod +x deploy_vps.sh
./deploy_vps.sh
```

### 4. **Start the Service**

```bash
sudo systemctl start telegram-bot-ram
sudo systemctl status telegram-bot-ram
```

## 🔧 Manual Deployment

### 1. **Create Directory Structure**

```bash
sudo mkdir -p /opt/telegram-bots/ram-tg-bot
sudo chown $USER:$USER /opt/telegram-bots/ram-tg-bot
cd /opt/telegram-bots/ram-tg-bot
```

### 2. **Copy Bot Files**

```bash
# Copy all bot files to the directory
cp -r /path/to/your/bot/files/* .
```

### 3. **Setup Python Environment**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. **Configure Bot**

```bash
# Create .env file
echo "TELEGRAM_BOT_TOKEN=your_bot_token_here" > .env

# Setup admin users
echo '[your_telegram_user_id]' > admins.json
```

### 5. **Create Systemd Service**

```bash
sudo tee /etc/systemd/system/telegram-bot-ram.service > /dev/null <<EOF
[Unit]
Description=Telegram Auto-Join Bot (Ram)
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/opt/telegram-bots/ram-tg-bot
Environment=PATH=/opt/telegram-bots/ram-tg-bot/venv/bin
ExecStart=/opt/telegram-bots/ram-tg-bot/venv/bin/python bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
```

### 6. **Enable and Start Service**

```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-bot-ram
sudo systemctl start telegram-bot-ram
```

## 📊 Service Management

### **Basic Commands**

```bash
# Start the service
sudo systemctl start telegram-bot-ram

# Stop the service
sudo systemctl stop telegram-bot-ram

# Restart the service
sudo systemctl restart telegram-bot-ram

# Check status
sudo systemctl status telegram-bot-ram

# View logs
sudo journalctl -u telegram-bot-ram -f

# View recent logs
sudo journalctl -u telegram-bot-ram --since "1 hour ago"
```

### **Multiple Bots Management**

If you have multiple bots, you can manage them easily:

```bash
# List all telegram bot services
sudo systemctl list-units --type=service | grep telegram-bot

# Start all telegram bots
sudo systemctl start telegram-bot-*

# Stop all telegram bots
sudo systemctl stop telegram-bot-*

# Restart all telegram bots
sudo systemctl restart telegram-bot-*
```

## 🔍 Monitoring and Logs

### **View Real-time Logs**

```bash
# Follow logs in real-time
sudo journalctl -u telegram-bot-ram -f

# View logs with timestamps
sudo journalctl -u telegram-bot-ram -o short-iso

# View logs from specific time
sudo journalctl -u telegram-bot-ram --since "2024-01-01 10:00:00"
```

### **Check Bot Status**

```bash
# Check if bot is running
ps aux | grep "python bot.py" | grep -v grep

# Check service status
sudo systemctl is-active telegram-bot-ram

# Check service logs
sudo journalctl -u telegram-bot-ram --no-pager -n 50
```

## 🛠️ Troubleshooting

### **Common Issues**

1. **Service won't start**
   ```bash
   # Check service logs
   sudo journalctl -u telegram-bot-ram -n 50
   
   # Check if bot token is set
   cat /opt/telegram-bots/ram-tg-bot/.env
   
   # Check if admin is configured
   cat /opt/telegram-bots/ram-tg-bot/admins.json
   ```

2. **Permission denied**
   ```bash
   # Fix ownership
   sudo chown -R $USER:$USER /opt/telegram-bots/ram-tg-bot
   
   # Fix permissions
   chmod +x /opt/telegram-bots/ram-tg-bot/bot.py
   ```

3. **Python dependencies missing**
   ```bash
   cd /opt/telegram-bots/ram-tg-bot
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### **Debug Mode**

To run the bot manually for debugging:

```bash
cd /opt/telegram-bots/ram-tg-bot
source venv/bin/activate
python bot.py
```

## 🔄 Updates and Maintenance

### **Update Bot Code**

```bash
# Stop the service
sudo systemctl stop telegram-bot-ram

# Backup current version
sudo cp -r /opt/telegram-bots/ram-tg-bot /opt/telegram-bots/ram-tg-bot_backup_$(date +%Y%m%d)

# Update code (git pull or manual copy)
cd /opt/telegram-bots/ram-tg-bot
git pull origin main

# Restart the service
sudo systemctl start telegram-bot-ram
```

### **Update Dependencies**

```bash
cd /opt/telegram-bots/ram-tg-bot
source venv/bin/activate
pip install --upgrade -r requirements.txt
sudo systemctl restart telegram-bot-ram
```

## 📁 File Structure

```
/opt/telegram-bots/ram-tg-bot/
├── bot.py                 # Main bot code
├── requirements.txt       # Python dependencies
├── .env                  # Bot token (create this)
├── admins.json           # Admin user IDs
├── channels.json         # Configured channels
├── welcome.txt           # Welcome message
├── schedule.txt          # Scheduled message
├── interval.txt          # Scheduling interval
├── logs.txt             # Join request logs
├── venv/                # Python virtual environment
├── deploy_vps.sh        # Deployment script
├── setup_vps.py         # Setup script
└── VPS_DEPLOYMENT.md    # This guide
```

## 🔒 Security Considerations

1. **File Permissions**
   ```bash
   # Secure sensitive files
   chmod 600 /opt/telegram-bots/ram-tg-bot/.env
   chmod 600 /opt/telegram-bots/ram-tg-bot/admins.json
   ```

2. **Firewall**
   ```bash
   # Ensure only necessary ports are open
   sudo ufw status
   ```

3. **Regular Backups**
   ```bash
   # Create backup script
   sudo cp -r /opt/telegram-bots/ram-tg-bot /backup/ram-tg-bot_$(date +%Y%m%d)
   ```

## 🎉 Success Checklist

- [ ] Bot token configured in `.env`
- [ ] Admin user ID added to `admins.json`
- [ ] Python virtual environment created
- [ ] Dependencies installed
- [ ] Systemd service created and enabled
- [ ] Service started successfully
- [ ] Bot responds to `/admin` command
- [ ] Bot can approve join requests
- [ ] Welcome messages are sent
- [ ] Logs are being generated

## 📞 Support

If you encounter issues:

1. Check the logs: `sudo journalctl -u telegram-bot-ram -f`
2. Verify configuration files
3. Test bot manually: `python bot.py`
4. Check service status: `sudo systemctl status telegram-bot-ram`

---

**Happy Botting! 🤖**
