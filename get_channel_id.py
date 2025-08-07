#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from telegram import Bot
import asyncio

# Load environment variables
load_dotenv()

async def get_channel_info():
    """Get channel information using the bot token"""
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in .env file")
        return
    
    bot = Bot(token)
    
    print("🔍 Channel ID Finder")
    print("=" * 30)
    print("This tool helps you find channel IDs.")
    print("\nMethods to get Channel ID:")
    print("1. Forward a message from your channel to @userinfobot")
    print("2. Use the /id command in your channel (if bot is admin)")
    print("3. Add bot to channel and check logs")
    print("4. Use @RawDataBot in your channel")
    
    print("\n📋 Common Channel ID formats:")
    print("• Public channels: -100xxxxxxxxxx")
    print("• Private channels: -100xxxxxxxxxx")
    print("• Supergroups: -100xxxxxxxxxx")
    
    # Test bot connection
    try:
        me = await bot.get_me()
        print(f"\n✅ Bot connected: @{me.username}")
        print(f"Bot ID: {me.id}")
    except Exception as e:
        print(f"❌ Error connecting to bot: {e}")
        return
    
    await bot.close()

if __name__ == "__main__":
    asyncio.run(get_channel_info())
