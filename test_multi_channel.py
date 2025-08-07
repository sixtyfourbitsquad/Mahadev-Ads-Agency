#!/usr/bin/env python3
"""
Test script for multi-channel message functionality
"""

import json
import os

def test_multi_channel_setup():
    """Test the multi-channel message setup"""
    
    print("🎯 Multi-Channel Message Test")
    print("=" * 40)
    
    # Check if channels.json exists
    if os.path.exists('channels.json'):
        with open('channels.json', 'r') as f:
            channels = json.load(f)
        print(f"✅ Found {len(channels)} configured channels")
        
        for channel_id, info in channels.items():
            print(f"   📢 {info['name']} (ID: {channel_id})")
    else:
        print("❌ No channels configured yet")
        print("   Please add channels using the bot first")
        return
    
    # Check if channel_messages.json exists
    if os.path.exists('channel_messages.json'):
        with open('channel_messages.json', 'r') as f:
            channel_messages = json.load(f)
        print(f"\n✅ Found channel-specific messages for {len(channel_messages)} channels")
        
        for channel_id, messages in channel_messages.items():
            channel_name = channels.get(channel_id, {}).get('name', 'Unknown')
            welcome = "✅" if "welcome" in messages else "❌"
            schedule = "✅" if "schedule" in messages else "❌"
            print(f"   📢 {channel_name}: Welcome {welcome} | Schedule {schedule}")
    else:
        print("\n❌ No channel-specific messages configured yet")
    
    print("\n🔧 How to use multi-channel messages:")
    print("1. Start the bot: python bot.py")
    print("2. Send /admin to your bot")
    print("3. Click '🎯 Channel Messages'")
    print("4. Select a channel and set welcome/schedule messages")
    print("5. Each channel can have different messages!")
    
    print("\n📋 Message Priority:")
    print("   Welcome Messages:")
    print("   1. Channel-specific welcome message")
    print("   2. Global welcome message")
    print("   3. Default welcome message")
    print("\n   Scheduled Messages:")
    print("   1. Channel-specific scheduled message")
    print("   2. Global scheduled message")
    print("   3. No message sent")

if __name__ == "__main__":
    test_multi_channel_setup()

