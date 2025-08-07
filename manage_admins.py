#!/usr/bin/env python3
"""
Admin Management Script for Telegram Bot
Easily add/remove admin users
"""

import json
import os
import sys

def load_admins():
    """Load current admin list"""
    if os.path.exists('admins.json'):
        with open('admins.json', 'r') as f:
            return json.load(f)
    return []

def save_admins(admins):
    """Save admin list to file"""
    with open('admins.json', 'w') as f:
        json.dump(admins, f, indent=2)

def show_current_admins():
    """Display current admin list"""
    admins = load_admins()
    if admins:
        print("👥 **Current Admins:**")
        for i, admin_id in enumerate(admins, 1):
            print(f"  {i}. {admin_id}")
    else:
        print("❌ No admins configured")
    return admins

def add_admin():
    """Add a new admin"""
    print("\n➕ **Add New Admin**")
    print("To find Telegram ID: Send /start to @userinfobot")
    
    try:
        admin_id = int(input("Enter Telegram user ID: ").strip())
        
        admins = load_admins()
        if admin_id in admins:
            print("⚠️  This admin already exists!")
            return
        
        admins.append(admin_id)
        save_admins(admins)
        print(f"✅ Admin {admin_id} added successfully!")
        
    except ValueError:
        print("❌ Please enter a valid number!")
    except Exception as e:
        print(f"❌ Error: {e}")

def remove_admin():
    """Remove an admin"""
    admins = show_current_admins()
    if not admins:
        return
    
    try:
        choice = int(input("\nEnter admin number to remove: ").strip())
        if 1 <= choice <= len(admins):
            removed_id = admins.pop(choice - 1)
            save_admins(admins)
            print(f"✅ Admin {removed_id} removed successfully!")
        else:
            print("❌ Invalid choice!")
    except ValueError:
        print("❌ Please enter a valid number!")
    except Exception as e:
        print(f"❌ Error: {e}")

def bulk_add_admins():
    """Add multiple admins at once"""
    print("\n👥 **Bulk Add Admins**")
    print("Enter multiple Telegram IDs separated by commas")
    print("Example: 123456789,987654321,555666777")
    
    try:
        admin_input = input("Enter Telegram user ID(s): ").strip()
        if not admin_input:
            print("❌ No input provided!")
            return
        
        # Parse multiple admin IDs
        new_admin_ids = [int(admin_id.strip()) for admin_id in admin_input.split(',') if admin_id.strip()]
        
        if not new_admin_ids:
            print("❌ No valid user IDs found!")
            return
        
        admins = load_admins()
        added_count = 0
        
        for admin_id in new_admin_ids:
            if admin_id not in admins:
                admins.append(admin_id)
                added_count += 1
            else:
                print(f"⚠️  Admin {admin_id} already exists, skipping...")
        
        save_admins(admins)
        print(f"✅ Added {added_count} new admin(s)!")
        
    except ValueError as e:
        print(f"❌ Invalid format: {e}")
        print("Please enter valid numbers separated by commas")
    except Exception as e:
        print(f"❌ Error: {e}")

def clear_all_admins():
    """Remove all admins"""
    print("\n🗑️  **Clear All Admins**")
    confirm = input("Are you sure you want to remove ALL admins? (yes/no): ").strip().lower()
    
    if confirm == 'yes':
        save_admins([])
        print("✅ All admins removed!")
    else:
        print("❌ Operation cancelled")

def main():
    """Main admin management interface"""
    print("🔧 **Telegram Bot Admin Management**")
    print("=" * 40)
    
    while True:
        print("\n📋 **Options:**")
        print("1. Show current admins")
        print("2. Add single admin")
        print("3. Add multiple admins")
        print("4. Remove admin")
        print("5. Clear all admins")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == '1':
            show_current_admins()
        elif choice == '2':
            add_admin()
        elif choice == '3':
            bulk_add_admins()
        elif choice == '4':
            remove_admin()
        elif choice == '5':
            clear_all_admins()
        elif choice == '6':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice! Please enter 1-6")

if __name__ == "__main__":
    main()
