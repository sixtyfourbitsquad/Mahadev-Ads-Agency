# 🚀 Quick Start Guide

## ⚡ 5-Minute Setup

### 1. Get Your Bot Token
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Follow instructions to create your bot
4. Copy the bot token (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Run Setup Script
```bash
python setup.py
```
- Enter your bot token when prompted
- Add your Telegram ID (get it from [@userinfobot](https://t.me/userinfobot))
- Configure welcome and scheduled messages

### 3. Add Bot to Your Group/Channel
1. Add your bot to your private group/channel
2. Make it an admin with these permissions:
   - ✅ **Invite Users via Link** (for groups)
   - ✅ **Approve Join Requests** (for channels)
   - ✅ **Send Messages** (for scheduled messages)

### 4. Start the Bot
```bash
python bot.py
```

### 5. Test the Admin Panel
Send `/admin` to your bot to access the admin panel!

## 🎯 What Happens Next

### For New Members:
- ✅ Join requests are automatically approved
- ✅ Welcome message sent via DM
- ✅ All actions logged for monitoring

### For Admins:
- 🔧 Use `/admin` to access control panel
- 📩 Set custom welcome messages
- ⏰ Configure scheduled messaging
- 📊 View join logs and statistics

## 🔧 Advanced Setup

### Environment Variables
Create `.env` file:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### Manual Configuration
Edit these files directly:
- `admins.json` - Add your Telegram ID
- `welcome.txt` - Custom welcome message
- `schedule.txt` - Scheduled message content
- `interval.txt` - Hours between scheduled messages

### Deployment Options

#### Option 1: Simple Run
```bash
python bot.py
```

#### Option 2: Using Deploy Script
```bash
chmod +x deploy.sh
./deploy.sh
```

#### Option 3: Systemd Service (Linux)
```bash
# Edit telegram-bot.service with your details
sudo cp telegram-bot.service /etc/systemd/system/
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

#### Option 4: PM2 (Node.js)
```bash
npm install -g pm2
pm2 start bot.py --name telegram-bot --interpreter python3
pm2 save
pm2 startup
```

## 🧪 Testing

Run the test script to verify everything is configured correctly:
```bash
python test_config.py
```

## 📚 Need Help?

- 📖 Read the full [README.md](README.md)
- 🔧 Check [example_extensions.py](example_extensions.py) for advanced features
- 🐛 Common issues in README troubleshooting section

## 🎉 You're Ready!

Your bot will now:
- ✅ Auto-approve join requests
- ✅ Send welcome DMs to new members
- ✅ Provide admin control panel
- ✅ Support scheduled messaging
- ✅ Log all activities

**Happy botting! 🤖**

