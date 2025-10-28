# VipPlay247 Bot - Deployment Guide

## 🚀 Pre-Deployment Checklist

### ✅ **Bot Status: READY FOR DEPLOYMENT**

All systems checked and verified:
- ✅ Bot renamed to VipPlay247Bot
- ✅ No syntax errors
- ✅ All imports working
- ✅ Batch approval system tested and working
- ✅ Configuration files present and valid
- ✅ Admin system functional
- ✅ Logging system active
- ✅ VipPlay247 branding applied

---

## 📋 **System Requirements**

### **Server Requirements:**
- **OS**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **RAM**: Minimum 512MB (1GB recommended)
- **Storage**: 1GB free space
- **Python**: 3.8+ (tested with 3.13)
- **Network**: Stable internet connection

### **Dependencies:**
```bash
python-telegram-bot==21.9
python-dotenv
httpx
```

---

## 🛠️ **VPS Deployment Steps**

### **1. Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv git -y

# Create deployment user (optional but recommended)
sudo useradd -m -s /bin/bash vipplay247
sudo usermod -aG sudo vipplay247
```

### **2. Deploy Bot Files**
```bash
# Clone or upload bot files
cd /home/vipplay247
git clone <your-repo> vipplay247-bot
# OR upload files manually

cd vipplay247-bot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### **3. Configuration**
```bash
# Set bot token
export TELEGRAM_BOT_TOKEN="8378914103:AAGur4uhkiDMisLdzDmddcD-x8TY83n6JDE"

# Or create .env file
echo "TELEGRAM_BOT_TOKEN=8378914103:AAGur4uhkiDMisLdzDmddcD-x8TY83n6JDE" > .env

# Verify admin configuration
cat admins.json
# Should contain: [1399652619]
```

### **4. Create Systemd Service**
```bash
sudo nano /etc/systemd/system/vipplay247-bot.service
```

**Service file content:**
```ini
[Unit]
Description=VipPlay247 Telegram Bot
After=network.target

[Service]
Type=simple
User=vipplay247
WorkingDirectory=/home/vipplay247/vipplay247-bot
Environment=TELEGRAM_BOT_TOKEN=8378914103:AAGur4uhkiDMisLdzDmddcD-x8TY83n6JDE
ExecStart=/home/vipplay247/vipplay247-bot/venv/bin/python bot_advanced.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### **5. Start and Enable Service**
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable vipplay247-bot

# Start service
sudo systemctl start vipplay247-bot

# Check status
sudo systemctl status vipplay247-bot
```

---

## 🎯 **Bot Commands & Features**

### **Admin Commands:**
- `/admin` - Access admin panel
- `/accept <number>` - Accept join requests (e.g., `/accept 5`)
- `/accept all` - Accept all pending requests
- `/pending` - Show pending users
- `/welcome` - Reply to user message to send welcome
- `/id` - Get chat ID (use in channels/groups)

### `/accept` date/range examples
You can approve join requests by specific dates or ranges using the `date` and `range` modes.

- `/accept date 2025-10-27` - Approves all join requests that were requested on 2025-10-27.
- `/accept range 2025-10-01 2025-10-15` - Approves all join requests whose join_date falls between (and including) 2025-10-01 and 2025-10-15.

Notes:
- Dates must be provided in `YYYY-MM-DD` format. The bot matches against the stored `join_date` (ISO format).
- Use `/accept all` to approve every pending request, or `/accept N` to approve the oldest N requests.

### **User Commands:**
- `/start` - Get welcome message

### **Welcome Message Buttons:**
- 🆔 **Get ID Now** - Registration/signup link
- 📹 **VipPlay247 Full Guide Video** - Tutorial video
- 📱 **Join VipPlay247 Telegram** - Telegram channel
- 📸 **Join VipPlay247 Instagram** - Instagram profile

---

## 📊 **Monitoring & Maintenance**

### **Check Bot Status:**
```bash
sudo systemctl status vipplay247-bot
```

### **View Logs:**
```bash
# System logs
sudo journalctl -u vipplay247-bot -f

# Bot activity logs
tail -f /home/vipplay247/vipplay247-bot/logs.txt
```

### **Restart Bot:**
```bash
sudo systemctl restart vipplay247-bot
```

### **Update Bot:**
```bash
cd /home/vipplay247/vipplay247-bot
source venv/bin/activate
git pull  # if using git
sudo systemctl restart vipplay247-bot
```

---

## 🔧 **Configuration Files**

### **Key Files:**
- `bot_advanced.py` - Main bot code
- `admins.json` - Admin user IDs
- `bot_config.json` - Bot configuration
- `users.json` - User database
- `logs.txt` - Activity logs
- `requirements.txt` - Dependencies

### **Admin Panel Configuration:**
1. Send `/admin` to bot
2. Configure URLs for each button
3. Set welcome message and image
4. Test with `/accept` command

---

## 🚨 **Troubleshooting**

### **Common Issues:**

**Bot not starting:**
```bash
# Check token
echo $TELEGRAM_BOT_TOKEN

# Check permissions
ls -la bot_advanced.py

# Check Python version
python3 --version
```

**Permission errors:**
```bash
chmod +x bot_advanced.py
chown vipplay247:vipplay247 -R /home/vipplay247/vipplay247-bot
```

**Dependencies issues:**
```bash
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

## 📱 **Bot Setup in Telegram**

### **Required Bot Permissions:**
- Send messages
- Read messages
- Manage chat (for join request detection)
- Add members (optional)

### **Channel Setup:**
1. Add bot as admin to your channel
2. Give "Manage Chat" permission
3. Test with a join request
4. Use `/accept 1` to approve

---

## ✅ **Deployment Verification**

### **Test Checklist:**
- [ ] Bot responds to `/start`
- [ ] Admin panel accessible with `/admin`
- [ ] Join requests are stored (not auto-approved)
- [ ] `/accept` command works
- [ ] Welcome messages sent after approval
- [ ] All buttons work in welcome message
- [ ] Logs are being written
- [ ] Service auto-restarts on failure

---

## 🎉 **Success!**

Your VipPlay247 Bot is now ready for production use!

**Support:** Check logs and systemd status for any issues.
**Updates:** Simply restart the service after code changes.
**Scaling:** Bot can handle hundreds of users simultaneously.
