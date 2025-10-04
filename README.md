# VipPlay247 Telegram Bot

Advanced Telegram bot for managing join requests with VipPlay247 branding and batch approval system.

## ???? Features

- **Batch Join Request Approval**: Use `/accept <number>` to approve multiple requests at once
- **VipPlay247 Branded Welcome**: Custom welcome messages with VipPlay247 buttons
- **Smart Button System**: Get ID, Guide Video, Telegram, and Instagram links
- **Admin Panel**: Easy configuration through Telegram commands
- **Comprehensive Logging**: Track all bot activities
- **File-based Storage**: No database required, uses JSON files

## ???? Quick Start

### Prerequisites

- Python 3.8+
- Telegram Bot Token (from @BotFather)
- Admin user ID

### Installation

1. Clone the repository:
```bash
git clone https://github.com/sixtyfourbitsquad/Mahadev-Ads-Agency.git
cd Mahadev-Ads-Agency
```

2. Install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure the bot:
```bash
# Copy example files
cp admins.json.example admins.json
cp bot_config.json.example bot_config.json

# Edit configuration
nano admins.json  # Add your user ID
```

4. Run the bot:
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
python bot_advanced.py
```

## ???? Usage

### Admin Commands

- `/admin` - Access the admin panel
- `/accept <number>` - Accept join requests (e.g., `/accept 5`)
- `/accept all` - Accept all pending requests
- `/pending` - Show pending users
- `/welcome` - Reply to user message to send welcome
- `/id` - Get chat ID (for groups/channels)

### User Commands

- `/start` - Get welcome message

### Welcome Message Buttons

- ???? **Get ID Now** - Registration/signup link
- ???? **VipPlay247 Full Guide Video** - Tutorial video
- ???? **Join VipPlay247 Telegram** - Telegram channel
- ???? **Join VipPlay247 Instagram** - Instagram profile

## ?????? Configuration

### Environment Variables

Set your bot token:
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

### Admin Configuration

Edit `admins.json`:
```json
[123456789]
```
Replace `123456789` with your Telegram user ID.

### Bot Settings

Configure through the admin panel (`/admin`) or edit `bot_config.json`:
```json
{
  "welcome_text": "Welcome to VipPlay247! ????",
  "signup_url": "https://your-signup-url.com",
  "join_group_url": "https://youtube.com/watch?v=your-guide-video",
  "download_apk": "https://t.me/your-telegram-channel",
  "daily_bonuses_url": "https://instagram.com/your-instagram"
}
```

## ???? How It Works

1. **User requests to join** your channel
2. **Bot stores the request** (doesn't auto-approve)
3. **You use `/accept <number>`** to approve requests in batches
4. **Bot automatically sends welcome messages** to approved users

## ???? File Structure

```
????????? bot_advanced.py                    # Main bot code
????????? requirements.txt                   # Python dependencies
????????? admins.json.example               # Admin configuration template
????????? bot_config.json.example           # Bot settings template
????????? final_verification.py             # Pre-deployment verification
????????? VipPlay247_DEPLOYMENT_GUIDE.md    # Deployment instructions
????????? README.md                         # This file
```

## ???? Deployment

### VPS Deployment

See `VipPlay247_DEPLOYMENT_GUIDE.md` for complete deployment instructions.

### Quick Deploy

```bash
# Run verification before deployment
python final_verification.py

# If all checks pass, deploy to your VPS
```

## ???? Verification

Before deployment, run:
```bash
python final_verification.py
```

## ???? Monitoring

### Check Bot Status
```bash
# View recent activity
tail -f logs.txt
```

## ??????? Troubleshooting

### Common Issues

1. **Bot not starting**
   - Check `TELEGRAM_BOT_TOKEN` is set
   - Run `python final_verification.py`

2. **Join requests not detected**
   - Ensure bot has "Manage Chat" permission
   - Bot must be admin in the channel

## ???? License

MIT License

## ???? Support

For support:
1. Check `logs.txt` for errors
2. Run `final_verification.py`
3. Open an issue on GitHub

## ???? Changelog

### v2.0.0 - VipPlay247 Edition
- Renamed to VipPlay247Bot
- Added batch approval system
- Updated branding to VipPlay247
- Added deployment guide
- Added verification script
