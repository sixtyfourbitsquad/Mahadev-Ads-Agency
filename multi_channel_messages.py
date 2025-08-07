#!/usr/bin/env python3
import json
import os

def manage_multi_channel_messages():
    """Manage different messages for different channels"""
    
    # Load current channels
    try:
        with open('channels.json', 'r') as f:
            channels = json.load(f)
    except FileNotFoundError:
        channels = {}
    
    # Load channel-specific messages
    try:
        with open('channel_messages.json', 'r') as f:
            channel_messages = json.load(f)
    except FileNotFoundError:
        channel_messages = {}
    
    print("🎯 Multi-Channel Message Manager")
    print("=" * 40)
    
    if not channels:
        print("❌ No channels configured yet!")
        print("Please add channels first using the bot or manual tool.")
        return
    
    while True:
        print(f"\n📋 Current Channels ({len(channels)}):")
        for i, (channel_id, info) in enumerate(channels.items(), 1):
            has_welcome = "✅" if channel_id in channel_messages and "welcome" in channel_messages[channel_id] else "❌"
            has_schedule = "✅" if channel_id in channel_messages and "schedule" in channel_messages[channel_id] else "❌"
            print(f"{i}. {info['name']} (ID: {channel_id})")
            print(f"   Welcome: {has_welcome} | Schedule: {has_schedule}")
        
        print("\n🔧 Options:")
        print("1. Set welcome message for a channel")
        print("2. Set scheduled message for a channel")
        print("3. View channel messages")
        print("4. Delete channel messages")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            set_welcome_message(channels, channel_messages)
        elif choice == "2":
            set_scheduled_message(channels, channel_messages)
        elif choice == "3":
            view_channel_messages(channels, channel_messages)
        elif choice == "4":
            delete_channel_messages(channels, channel_messages)
        elif choice == "5":
            break
        else:
            print("❌ Invalid choice!")

def set_welcome_message(channels, channel_messages):
    """Set welcome message for a specific channel"""
    print("\n📩 Set Welcome Message")
    print("-" * 20)
    
    # Show channels
    channel_list = list(channels.items())
    for i, (channel_id, info) in enumerate(channel_list, 1):
        print(f"{i}. {info['name']} (ID: {channel_id})")
    
    try:
        choice = int(input("\nSelect channel (number): ")) - 1
        if 0 <= choice < len(channel_list):
            channel_id, info = channel_list[choice]
            
            print(f"\nSetting welcome message for: {info['name']}")
            print("Note: This will be a text message. For media messages, use the bot directly.")
            
            message = input("Enter welcome message: ").strip()
            
            if message:
                if channel_id not in channel_messages:
                    channel_messages[channel_id] = {}
                
                channel_messages[channel_id]["welcome"] = {
                    "type": "text",
                    "content": message
                }
                
                save_channel_messages(channel_messages)
                print(f"✅ Welcome message set for {info['name']}!")
            else:
                print("❌ Message cannot be empty!")
        else:
            print("❌ Invalid channel number!")
    except ValueError:
        print("❌ Please enter a valid number!")

def set_scheduled_message(channels, channel_messages):
    """Set scheduled message for a specific channel"""
    print("\n🕒 Set Scheduled Message")
    print("-" * 20)
    
    # Show channels
    channel_list = list(channels.items())
    for i, (channel_id, info) in enumerate(channel_list, 1):
        print(f"{i}. {info['name']} (ID: {channel_id})")
    
    try:
        choice = int(input("\nSelect channel (number): ")) - 1
        if 0 <= choice < len(channel_list):
            channel_id, info = channel_list[choice]
            
            print(f"\nSetting scheduled message for: {info['name']}")
            print("Note: This will be a text message. For media messages, use the bot directly.")
            
            message = input("Enter scheduled message: ").strip()
            
            if message:
                if channel_id not in channel_messages:
                    channel_messages[channel_id] = {}
                
                channel_messages[channel_id]["schedule"] = {
                    "type": "text",
                    "content": message
                }
                
                save_channel_messages(channel_messages)
                print(f"✅ Scheduled message set for {info['name']}!")
            else:
                print("❌ Message cannot be empty!")
        else:
            print("❌ Invalid channel number!")
    except ValueError:
        print("❌ Please enter a valid number!")

def view_channel_messages(channels, channel_messages):
    """View messages for all channels"""
    print("\n📋 Channel Messages")
    print("-" * 20)
    
    for channel_id, info in channels.items():
        print(f"\n📢 {info['name']} (ID: {channel_id})")
        
        if channel_id in channel_messages:
            if "welcome" in channel_messages[channel_id]:
                welcome = channel_messages[channel_id]["welcome"]
                print(f"   📩 Welcome: {welcome.get('content', 'N/A')}")
            else:
                print("   📩 Welcome: ❌ Not set")
            
            if "schedule" in channel_messages[channel_id]:
                schedule = channel_messages[channel_id]["schedule"]
                print(f"   🕒 Schedule: {schedule.get('content', 'N/A')}")
            else:
                print("   🕒 Schedule: ❌ Not set")
        else:
            print("   📩 Welcome: ❌ Not set")
            print("   🕒 Schedule: ❌ Not set")

def delete_channel_messages(channels, channel_messages):
    """Delete messages for a specific channel"""
    print("\n🗑️ Delete Channel Messages")
    print("-" * 20)
    
    # Show channels
    channel_list = list(channels.items())
    for i, (channel_id, info) in enumerate(channel_list, 1):
        print(f"{i}. {info['name']} (ID: {channel_id})")
    
    try:
        choice = int(input("\nSelect channel (number): ")) - 1
        if 0 <= choice < len(channel_list):
            channel_id, info = channel_list[choice]
            
            print(f"\nDeleting messages for: {info['name']}")
            print("1. Delete welcome message only")
            print("2. Delete scheduled message only")
            print("3. Delete both messages")
            
            delete_choice = input("Enter choice (1-3): ").strip()
            
            if channel_id in channel_messages:
                if delete_choice == "1":
                    if "welcome" in channel_messages[channel_id]:
                        del channel_messages[channel_id]["welcome"]
                        print("✅ Welcome message deleted!")
                    else:
                        print("❌ No welcome message to delete!")
                
                elif delete_choice == "2":
                    if "schedule" in channel_messages[channel_id]:
                        del channel_messages[channel_id]["schedule"]
                        print("✅ Scheduled message deleted!")
                    else:
                        print("❌ No scheduled message to delete!")
                
                elif delete_choice == "3":
                    del channel_messages[channel_id]
                    print("✅ All messages deleted!")
                
                else:
                    print("❌ Invalid choice!")
                
                save_channel_messages(channel_messages)
            else:
                print("❌ No messages found for this channel!")
        else:
            print("❌ Invalid channel number!")
    except ValueError:
        print("❌ Please enter a valid number!")

def save_channel_messages(channel_messages):
    """Save channel messages to file"""
    with open('channel_messages.json', 'w') as f:
        json.dump(channel_messages, f, indent=2)

if __name__ == "__main__":
    manage_multi_channel_messages()
