#!/usr/bin/env python3
"""
Create .env file for Telegram Bot
"""

import os

def create_env_file():
    """Create .env file with bot token"""
    print("🔑 Creating .env file for Telegram Bot")
    print("=" * 40)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/n): ").strip().lower()
        if overwrite != 'y':
            print("❌ Operation cancelled.")
            return
    
    # Get bot token
    print("\n📋 To get your bot token:")
    print("1. Message @BotFather on Telegram")
    print("2. Send /newbot")
    print("3. Follow the instructions")
    print("4. Copy the token (looks like: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz)")
    print()
    
    token = input("Enter your bot token: ").strip()
    
    if not token:
        print("❌ Bot token is required!")
        return
    
    # Validate token format (basic check)
    if ':' not in token or len(token) < 20:
        print("⚠️  Warning: Token format doesn't look correct.")
        print("Expected format: 123456789:ABCdefGHIjklMNOpqrsTUVwxyz")
        continue_anyway = input("Continue anyway? (y/n): ").strip().lower()
        if continue_anyway != 'y':
            return
    
    # Create .env file
    try:
        with open('.env', 'w') as f:
            f.write(f"TELEGRAM_BOT_TOKEN={token}\n")
        
        print("✅ .env file created successfully!")
        print(f"Token saved: {token[:10]}...{token[-10:]}")
        
        # Test if token is accessible
        os.environ['TELEGRAM_BOT_TOKEN'] = token
        print("✅ Environment variable set for testing")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return
    
    print("\n🎉 Setup complete!")
    print("You can now run: python bot.py")

if __name__ == "__main__":
    create_env_file()

