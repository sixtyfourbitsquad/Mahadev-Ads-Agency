# 🤖 Telegram Auto-Join Bot

A powerful Telegram bot that automatically approves join requests, sends welcome messages, and provides an admin panel for managing scheduled messages.

## ✨ Features

- **🔄 Auto-Join Request Approval**: Instantly approves join requests to private groups/channels
- **💬 Welcome Messages**: Sends personalized welcome DMs to new members
- **🔧 Admin Panel**: Full-featured inline button-based admin interface
- **⏰ Scheduled Messaging**: Automated message scheduling with customizable intervals
- **📊 Logging**: Comprehensive logging of all join requests and DM attempts
- **💾 File-Based Storage**: No database required - everything stored in simple text/JSON files

## 🛠️ Admin Panel Features

### 📩 Welcome Message Management
- Set custom welcome messages
- Preview current welcome message
- Instant updates via inline buttons

### 🕒 Scheduled Messaging
- Set custom scheduled messages
- Choose from multiple intervals (1h, 3h, 5h, 12h, 24h)
- Start/stop scheduler with one click
- Preview scheduled messages

### 📑 Logging & Monitoring
- View recent join logs
- Track DM success/failure rates
- Monitor bot activity

## 🚀 Quick Setup

### 1. Prerequisites
- Python 3.10 or higher
- A Telegram bot token (get from [@BotFather](https://t.me/BotFather))
- Admin access to a private group/channel

### 2. Installation

```bash
# Clone or download the bot files
# Navigate to the bot directory
cd telegram-auto-join-bot

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

#### Set Bot Token
Set your bot token as an environment variable:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

Or create a `.env` file:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

#### Add Admin Users
Edit `admins.json` and add your Telegram user ID:

```json
[123456789, 987654321]
```

To find your Telegram ID:
1. Send `/start` to [@userinfobot](https://t.me/userinfobot)
2. Copy your user ID and add it to `admins.json`

#### Configure Bot for Group/Channel
1. Add your bot to your private group/channel
2. Make the bot an admin with these permissions:
   - **Invite Users via Link** (for groups)
   - **Approve Join Requests** (for channels)
   - **Send Messages** (for scheduled messages)

### 4. Run the Bot

```bash
python bot.py
```

## 📁 File Structure

```
telegram-auto-join-bot/
├── bot.py              # Main bot code
├── requirements.txt     # Python dependencies
├── admins.json         # Admin user IDs
├── welcome.txt         # Welcome message
├── schedule.txt        # Scheduled message
├── interval.txt        # Scheduling interval (hours)
├── logs.txt           # Join request logs
└── README.md          # This file
```

## 🎮 Usage

### For Regular Users
- The bot automatically approves join requests
- New members receive welcome DMs automatically
- No user interaction required

### For Admins
1. Send `/admin` to the bot
2. Use the inline button interface to:
   - Set welcome messages
   - Configure scheduled messages
   - View logs
   - Manage scheduler

## 🔧 Admin Panel Guide

### 📩 Set Welcome Message
1. Click "📩 Set Welcome Message"
2. Send your new welcome message
3. Bot saves and confirms

### 🕒 Set Scheduled Message
1. Click "🕒 Set Scheduled Message"
2. Send your scheduled message
3. Bot saves and confirms

### ⏱ Set Interval
1. Click "⏱ Set Interval"
2. Choose from available intervals
3. Bot updates and confirms

### 🔁 Toggle Scheduler
- Click to start/stop scheduled messaging
- Button text changes dynamically
- Shows current status

### 📑 View Logs
- Shows last 10 join requests
- Displays DM success/failure status
- Includes timestamps and user info

## 🔒 Security Features

- **Admin-only access**: Only users in `admins.json` can access admin panel
- **Error handling**: Graceful handling of failed DMs and permissions
- **Logging**: All actions logged for audit trail
- **File validation**: Automatic creation of missing config files

## 🚨 Troubleshooting

### Bot not approving join requests?
- Ensure bot is admin in the group/channel
- Check bot has "Approve Join Requests" permission
- Verify bot token is correct

### Welcome messages not sending?
- Users may have privacy settings preventing DMs
- Check logs.txt for error details
- Bot will log failed attempts

### Admin panel not working?
- Verify your user ID is in `admins.json`
- Check bot token environment variable
- Ensure bot is running

### Scheduled messages not sending?
- Check if scheduler is started
- Verify interval.txt contains valid number
- Check bot permissions in target groups

## 🔄 Auto-Restart Setup

### Using systemd (Linux)
Create `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Telegram Auto-Join Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/bot
Environment=TELEGRAM_BOT_TOKEN=your_token
ExecStart=/usr/bin/python3 bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### Using PM2 (Node.js)
```bash
npm install -g pm2
pm2 start bot.py --name telegram-bot --interpreter python3
pm2 save
pm2 startup
```

## 📝 Customization

### Adding More Intervals
Edit the `show_interval_options` method in `bot.py` to add more interval options.

### Custom Welcome Messages
Edit `welcome.txt` directly or use the admin panel.

### Scheduled Message Targets
Modify the `send_scheduled_message` method to target specific groups/channels.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

This project is open source and available under the MIT License.

---

**Made with ❤️ for Telegram communities**

