#!/usr/bin/env python3
"""
Setup script for Telegram Auto-Join Bot
Helps users configure the bot quickly
"""

import json
import os
import sys

def create_env_file():
    """Create .env file with bot token"""
    print("\n📋 To get your bot token:")
    print("1. Message @BotFather on Telegram")
    print("2. Send /newbot")
    print("3. Follow the instructions")
    print("4. Copy the token (looks like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)")
    print()
    
    token = input("Enter your Telegram bot token: ").strip()
    
    if not token:
        print("❌ Bot token is required!")
        return False
    
    # Validate token format (basic check)
    if ':' not in token or len(token) < 20:
        print("⚠️  Warning: Token format doesn't look correct.")
        print("Expected format: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
        continue_anyway = input("Continue anyway? (y/n): ").strip().lower()
        if continue_anyway != 'y':
            return False
        
    with open('.env', 'w') as f:
        f.write(f"TELEGRAM_BOT_TOKEN={token}\n")
    
    print("✅ .env file created successfully!")
    print(f"Token saved: {token[:10]}...{token[-10:]}")
    return True

def setup_admins():
    """Setup admin users"""
    print("\n📋 Admin Setup")
    print("To find your Telegram ID, send /start to @userinfobot")
    
    admins = []
    while True:
        user_id = input("Enter admin Telegram ID (or 'done' to finish): ").strip()
        
        if user_id.lower() == 'done':
            break
            
        try:
            user_id = int(user_id)
            admins.append(user_id)
            print(f"✅ Added admin ID: {user_id}")
        except ValueError:
            print("❌ Invalid ID. Please enter a number.")
    
    with open('admins.json', 'w') as f:
        json.dump(admins, f, indent=2)
    
    print(f"✅ {len(admins)} admin(s) configured!")

def setup_welcome_message():
    """Setup welcome message"""
    print("\n💬 Welcome Message Setup")
    print("Current welcome message:")
    
    try:
        with open('welcome.txt', 'r', encoding='utf-8') as f:
            current = f.read()
            print(f"'{current}'")
    except FileNotFoundError:
        current = "Welcome to our group! 🎉\n\nWe're glad to have you here. Please read the rules and enjoy your stay!"
        print(f"'{current}'")
    
    change = input("Do you want to change the welcome message? (y/n): ").strip().lower()
    
    if change == 'y':
        print("Enter your new welcome message (press Enter twice to finish):")
        lines = []
        while True:
            line = input()
            if line == "" and lines and lines[-1] == "":
                break
            lines.append(line)
        
        new_message = '\n'.join(lines[:-1])  # Remove the last empty line
        
        with open('welcome.txt', 'w', encoding='utf-8') as f:
            f.write(new_message)
        
        print("✅ Welcome message updated!")

def setup_scheduled_message():
    """Setup scheduled message"""
    print("\n⏰ Scheduled Message Setup")
    print("Current scheduled message:")
    
    try:
        with open('schedule.txt', 'r', encoding='utf-8') as f:
            current = f.read()
            print(f"'{current}'")
    except FileNotFoundError:
        current = "📢 Reminder: Don't forget to check the latest updates in our group!"
        print(f"'{current}'")
    
    change = input("Do you want to change the scheduled message? (y/n): ").strip().lower()
    
    if change == 'y':
        print("Enter your new scheduled message:")
        new_message = input().strip()
        
        with open('schedule.txt', 'w', encoding='utf-8') as f:
            f.write(new_message)
        
        print("✅ Scheduled message updated!")

def setup_interval():
    """Setup scheduling interval"""
    print("\n⏱ Interval Setup")
    print("Current interval: 24 hours")
    
    change = input("Do you want to change the interval? (y/n): ").strip().lower()
    
    if change == 'y':
        print("Available intervals:")
        print("1. 1 hour")
        print("2. 3 hours")
        print("3. 5 hours")
        print("4. 12 hours")
        print("5. 24 hours")
        
        choice = input("Enter your choice (1-5): ").strip()
        
        intervals = {1: 1, 2: 3, 3: 5, 4: 12, 5: 24}
        
        if choice in intervals:
            interval = intervals[int(choice)]
            with open('interval.txt', 'w') as f:
                f.write(str(interval))
            print(f"✅ Interval updated to {interval} hours!")
        else:
            print("❌ Invalid choice. Using default 24 hours.")

def show_instructions():
    """Show post-setup instructions"""
    print("\n" + "="*50)
    print("🎉 Setup Complete!")
    print("="*50)
    print("\n📋 Next Steps:")
    print("1. Add your bot to your private group/channel")
    print("2. Make the bot an admin with these permissions:")
    print("   - Invite Users via Link (for groups)")
    print("   - Approve Join Requests (for channels)")
    print("   - Send Messages (for scheduled messages)")
    print("3. Run the bot: python bot.py")
    print("4. Test the admin panel: send /admin to your bot")
    print("\n📚 For more help, check the README.md file")

def main():
    """Main setup function"""
    print("🤖 Telegram Auto-Join Bot Setup")
    print("="*40)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        if not create_env_file():
            return
    
    # Setup admins
    setup_admins()
    
    # Setup messages
    setup_welcome_message()
    setup_scheduled_message()
    setup_interval()
    
    # Show instructions
    show_instructions()

if __name__ == "__main__":
    main()
