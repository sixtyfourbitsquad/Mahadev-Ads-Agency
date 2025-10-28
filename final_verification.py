#!/usr/bin/env python3
"""
VipPlay247 Bot - Final Verification Script
Run this before deployment to ensure everything is ready
"""

import os
import json
import sys
import subprocess
from datetime import datetime

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\n📦 Checking dependencies...")
    try:
        import telegram
        print(f"✅ python-telegram-bot {telegram.__version__}")
        
        import dotenv
        print("✅ python-dotenv installed")
        
        import httpx
        print(f"✅ httpx {httpx.__version__}")
        
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def check_syntax():
    """Check bot code for syntax errors"""
    print("\n🔍 Checking syntax...")
    try:
        result = subprocess.run(['python', '-m', 'py_compile', 'bot_advanced.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ No syntax errors found")
            return True
        else:
            print(f"❌ Syntax errors: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking syntax: {e}")
        return False

def check_config_files():
    """Check configuration files"""
    print("\n📁 Checking configuration files...")
    
    required_files = {
        'admins.json': 'Admin configuration',
        'bot_config.json': 'Bot settings',
        'requirements.txt': 'Dependencies list'
    }
    
    all_good = True
    
    for file, description in required_files.items():
        if os.path.exists(file):
            print(f"✅ {file} - {description}")
            
            # Validate JSON files
            if file.endswith('.json'):
                try:
                    with open(file, 'r') as f:
                        json.load(f)
                    print(f"   ✅ Valid JSON format")
                except json.JSONDecodeError:
                    print(f"   ❌ Invalid JSON format")
                    all_good = False
        else:
            print(f"❌ {file} - Missing")
            all_good = False
    
    return all_good

def check_bot_token():
    """Check if bot token is configured"""
    print("\n🔑 Checking bot token...")
    
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        if len(token) > 40 and ':' in token:
            print("✅ Bot token configured and valid format")
            return True
        else:
            print("❌ Bot token format invalid")
            return False
    else:
        print("❌ TELEGRAM_BOT_TOKEN environment variable not set")
        return False

def check_admin_config():
    """Check admin configuration"""
    print("\n👑 Checking admin configuration...")
    
    try:
        with open('admins.json', 'r') as f:
            admins = json.load(f)
        
        if isinstance(admins, list) and len(admins) > 0:
            print(f"✅ {len(admins)} admin(s) configured: {admins}")
            return True
        else:
            print("❌ No admins configured")
            return False
    except Exception as e:
        print(f"❌ Error reading admin config: {e}")
        return False

def check_bot_config():
    """Check bot configuration"""
    print("\n⚙️ Checking bot configuration...")
    
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        required_keys = ['welcome_text', 'signup_url', 'join_group_url', 'download_apk', 'daily_bonuses_url']
        
        for key in required_keys:
            if key in config:
                value = config[key]
                if value:
                    print(f"✅ {key}: Configured")
                else:
                    print(f"⚠️ {key}: Not set (optional)")
            else:
                print(f"❌ {key}: Missing from config")
        
        return True
    except Exception as e:
        print(f"❌ Error reading bot config: {e}")
        return False

def check_permissions():
    """Check file permissions"""
    print("\n🔒 Checking file permissions...")
    
    if os.access('bot_advanced.py', os.R_OK):
        print("✅ bot_advanced.py is readable")
        return True
    else:
        print("❌ bot_advanced.py permission issues")
        return False

def check_users_join_date():
    """Verify users.json entries include a parsable join_date key"""
    print("\n📅 Checking users' join_date fields...")
    if not os.path.exists('users.json'):
        print("❌ users.json - Missing")
        return False

    try:
        with open('users.json', 'r') as f:
            users = json.load(f)
        if not isinstance(users, dict):
            print("❌ users.json - Unexpected format (expected object/dict)")
            return False

        problems = 0
        for uid, data in users.items():
            jd = data.get('join_date') or data.get('joined_date')
            if not jd:
                print(f"❌ User {uid} - missing 'join_date'")
                problems += 1
                continue
            try:
                # validate ISO format
                datetime.fromisoformat(jd)
            except Exception:
                print(f"❌ User {uid} - invalid join_date format: {jd}")
                problems += 1

        if problems == 0:
            print(f"✅ All users have valid join_date fields ({len(users)} users)")
            return True
        else:
            print(f"❌ Found {problems} user(s) with missing/invalid join_date")
            return False
    except Exception as e:
        print(f"❌ Error reading users.json: {e}")
        return False

def main():
    """Run all verification checks"""
    print("🤖 VipPlay247 Bot - Final Verification")
    print("=" * 50)
    
    checks = [
        check_python_version,
        check_dependencies,
        check_syntax,
        check_config_files,
        check_users_join_date,
        check_bot_token,
        check_admin_config,
        check_bot_config,
        check_permissions
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Verification Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 ✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT!")
        print("\n🚀 Next steps:")
        print("1. Upload bot files to your VPS")
        print("2. Follow VipPlay247_DEPLOYMENT_GUIDE.md")
        print("3. Set up systemd service")
        print("4. Start the bot!")
        return True
    else:
        print("❌ Some checks failed - please fix issues before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
