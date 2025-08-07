#!/usr/bin/env python3
"""
VPS Setup Script for Telegram Bot
Helps configure the bot for VPS deployment
"""

import json
import os
import sys

def create_env_file():
    """Create .env file with bot token"""
    print("🔑 Setting up bot token...")
    
    if os.path.exists('.env'):
        overwrite = input("⚠️  .env file already exists! Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("❌ Setup cancelled.")
            return False
    
    print("\n📋 To get your bot token:")
    print("1. Message @BotFather on Telegram")
    print("2. Send /newbot")
    print("3. Follow the instructions")
    print("4. Copy the token (looks like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)")
    print()
    
    token = input("Enter your bot token: ").strip()
    
    if not token:
        print("❌ Bot token is required!")
        return False
    
    # Validate token format
    if ':' not in token or len(token) < 20:
        print("⚠️  Warning: Token format doesn't look correct.")
        print("Expected format: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
        continue_anyway = input("Continue anyway? (y/n): ").strip().lower()
        if continue_anyway != 'y':
            return False
    
    # Create .env file
    try:
        with open('.env', 'w') as f:
            f.write(f"TELEGRAM_BOT_TOKEN={token}\n")
        
        print("✅ .env file created successfully!")
        print(f"Token saved: {token[:10]}...{token[-10:]}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def setup_admins():
    """Setup admin users"""
    print("\n👥 Setting up admin users...")
    
    if os.path.exists('admins.json'):
        overwrite = input("⚠️  admins.json already exists! Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("❌ Admin setup cancelled.")
            return False
    
    print("\n📋 To find your Telegram ID:")
    print("1. Send /start to @userinfobot on Telegram")
    print("2. Copy your user ID (number)")
    print()
    
    admin_id = input("Enter your Telegram user ID: ").strip()
    
    if not admin_id.isdigit():
        print("❌ User ID must be a number!")
        return False
    
    try:
        admins = [int(admin_id)]
        with open('admins.json', 'w') as f:
            json.dump(admins, f, indent=2)
        
        print("✅ Admin users configured!")
        print(f"Admin ID: {admin_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating admins.json: {e}")
        return False

def create_default_files():
    """Create default configuration files"""
    print("\n📝 Creating default configuration files...")
    
    # Create welcome message
    if not os.path.exists('welcome.txt'):
        with open('welcome.txt', 'w', encoding='utf-8') as f:
            f.write("Welcome to our group! 🎉\n\nWe're glad to have you here. Please read the rules and enjoy your stay!")
        print("✅ welcome.txt created")
    
    # Create scheduled message
    if not os.path.exists('schedule.txt'):
        with open('schedule.txt', 'w', encoding='utf-8') as f:
            f.write("📢 Reminder: Don't forget to check the latest updates in our group!")
        print("✅ schedule.txt created")
    
    # Create interval file
    if not os.path.exists('interval.txt'):
        with open('interval.txt', 'w') as f:
            f.write("24")
        print("✅ interval.txt created")
    
    # Create logs file
    if not os.path.exists('logs.txt'):
        with open('logs.txt', 'w', encoding='utf-8') as f:
            f.write("")
        print("✅ logs.txt created")
    
    # Create channels file
    if not os.path.exists('channels.json'):
        with open('channels.json', 'w') as f:
            json.dump({}, f, indent=2)
        print("✅ channels.json created")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Telegram Bot VPS Setup")
    print("=" * 40)
    
    success = True
    
    # Create default files
    if not create_default_files():
        success = False
    
    # Setup bot token
    if not create_env_file():
        success = False
    
    # Setup admins
    if not setup_admins():
        success = False
    
    if success:
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Add your bot to your channels/groups")
        print("2. Make the bot an admin with required permissions")
        print("3. Test the bot by sending /admin")
        print("\n🔧 For VPS deployment:")
        print("1. Run: chmod +x deploy_vps.sh")
        print("2. Run: ./deploy_vps.sh")
        print("3. Start the service: sudo systemctl start telegram-bot-ram")
    else:
        print("\n❌ Setup failed! Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
