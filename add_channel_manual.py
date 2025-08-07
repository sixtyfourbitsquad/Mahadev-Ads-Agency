#!/usr/bin/env python3
import json
import os

def add_channel_manually():
    """Manually add a channel to the bot configuration"""
    
    # Load current channels
    try:
        with open('channels.json', 'r') as f:
            channels = json.load(f)
    except FileNotFoundError:
        channels = {}
    
    print("🔧 Manual Channel Addition Tool")
    print("=" * 40)
    
    # Get channel information
    channel_id = input("Enter Channel ID (e.g., -1001234567890): ").strip()
    channel_name = input("Enter Channel Name: ").strip()
    channel_type = input("Enter Channel Type (channel/supergroup): ").strip()
    username = input("Enter Channel Username (without @, or press Enter if private): ").strip()
    
    if not username:
        username = None
    
    # Add channel to configuration
    channels[channel_id] = {
        "name": channel_name,
        "type": channel_type,
        "username": username
    }
    
    # Save to file
    with open('channels.json', 'w') as f:
        json.dump(channels, f, indent=2)
    
    print(f"\n✅ Channel '{channel_name}' added successfully!")
    print(f"Channel ID: {channel_id}")
    print(f"Type: {channel_type}")
    print(f"Username: {username or 'None (Private)'}")
    
    # Show all channels
    print("\n📋 Current Channels:")
    for cid, info in channels.items():
        print(f"• {info['name']} (ID: {cid})")

if __name__ == "__main__":
    add_channel_manually()
