#!/usr/bin/env python3
"""
Test script for Telegram Auto-Join Bot
Verifies configuration and dependencies
"""

import json
import os
import sys

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, continue without it
    pass

def test_dependencies():
    """Test if all required packages are installed"""
    print("🔍 Testing dependencies...")
    
    required_packages = [
        'telegram',
        'apscheduler'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed!")
    return True

def test_config_files():
    """Test if all configuration files exist"""
    print("\n📁 Testing configuration files...")
    
    required_files = [
        'admins.json',
        'welcome.txt',
        'schedule.txt',
        'interval.txt'
    ]
    
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - missing")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        print("Run: python setup.py")
        return False
    
    print("✅ All config files exist!")
    return True

def test_env_variable():
    """Test if bot token is set"""
    print("\n🔑 Testing environment variables...")
    
    # Check if .env file exists
    if os.path.exists('.env'):
        print("✅ .env file exists")
    else:
        print("❌ .env file not found")
        print("Run: python create_env.py or python setup.py")
        return False
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if token:
        print("✅ TELEGRAM_BOT_TOKEN is set")
        print(f"Token: {token[:10]}...{token[-10:]}")
        return True
    else:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        print("Create .env file with: TELEGRAM_BOT_TOKEN=your_token")
        return False

def test_admin_config():
    """Test admin configuration"""
    print("\n👥 Testing admin configuration...")
    
    try:
        with open('admins.json', 'r') as f:
            admins = json.load(f)
        
        if isinstance(admins, list) and len(admins) > 0:
            print(f"✅ {len(admins)} admin(s) configured")
            return True
        else:
            print("❌ No admins configured")
            print("Edit admins.json and add your Telegram ID")
            return False
    except Exception as e:
        print(f"❌ Error reading admins.json: {e}")
        return False

def test_messages():
    """Test message files"""
    print("\n💬 Testing message files...")
    
    try:
        with open('welcome.txt', 'r', encoding='utf-8') as f:
            welcome = f.read().strip()
        
        if welcome:
            print("✅ Welcome message configured")
        else:
            print("❌ Welcome message is empty")
            return False
    except Exception as e:
        print(f"❌ Error reading welcome.txt: {e}")
        return False
    
    try:
        with open('schedule.txt', 'r', encoding='utf-8') as f:
            schedule = f.read().strip()
        
        if schedule:
            print("✅ Scheduled message configured")
        else:
            print("❌ Scheduled message is empty")
            return False
    except Exception as e:
        print(f"❌ Error reading schedule.txt: {e}")
        return False
    
    return True

def test_interval():
    """Test interval configuration"""
    print("\n⏱ Testing interval configuration...")
    
    try:
        with open('interval.txt', 'r') as f:
            interval = int(f.read().strip())
        
        if 1 <= interval <= 168:  # 1 hour to 1 week
            print(f"✅ Interval set to {interval} hours")
            return True
        else:
            print(f"❌ Invalid interval: {interval} hours")
            return False
    except Exception as e:
        print(f"❌ Error reading interval.txt: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Telegram Auto-Join Bot Configuration Test")
    print("=" * 50)
    
    tests = [
        test_dependencies,
        test_config_files,
        test_env_variable,
        test_admin_config,
        test_messages,
        test_interval
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your bot is ready to run.")
        print("Run: python bot.py")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("Run: python setup.py to configure the bot")

if __name__ == "__main__":
    main()
