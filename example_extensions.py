#!/usr/bin/env python3
"""
Example extensions for the Telegram Auto-Join Bot
This file shows how to extend the bot with additional features
"""

import json
import os
from typing import List

# Example: Add group targeting for scheduled messages
class GroupTargetingExtension:
    """Extension to target specific groups for scheduled messages"""
    
    def __init__(self):
        self.groups_file = "target_groups.json"
        self.load_groups()
    
    def load_groups(self):
        """Load target groups from file"""
        if os.path.exists(self.groups_file):
            with open(self.groups_file, 'r') as f:
                self.target_groups = json.load(f)
        else:
            self.target_groups = []
            self.save_groups()
    
    def save_groups(self):
        """Save target groups to file"""
        with open(self.groups_file, 'w') as f:
            json.dump(self.target_groups, f, indent=2)
    
    def add_group(self, group_id: int, group_name: str):
        """Add a group to the target list"""
        group_info = {
            "id": group_id,
            "name": group_name,
            "active": True
        }
        
        # Check if group already exists
        for group in self.target_groups:
            if group["id"] == group_id:
                group.update(group_info)
                self.save_groups()
                return True
        
        self.target_groups.append(group_info)
        self.save_groups()
        return True
    
    def remove_group(self, group_id: int):
        """Remove a group from the target list"""
        self.target_groups = [g for g in self.target_groups if g["id"] != group_id]
        self.save_groups()
    
    def get_active_groups(self) -> List[dict]:
        """Get list of active target groups"""
        return [g for g in self.target_groups if g["active"]]

# Example: Add message templates
class MessageTemplates:
    """Extension for managing message templates"""
    
    def __init__(self):
        self.templates_file = "templates.json"
        self.load_templates()
    
    def load_templates(self):
        """Load message templates from file"""
        if os.path.exists(self.templates_file):
            with open(self.templates_file, 'r') as f:
                self.templates = json.load(f)
        else:
            self.templates = {
                "welcome": {
                    "default": "Welcome to our group! 🎉\n\nWe're glad to have you here.",
                    "premium": "Welcome to our premium group! 🌟\n\nYou have access to exclusive content.",
                    "newbie": "Welcome new member! 👋\n\nPlease read our rules and introduce yourself."
                },
                "schedule": {
                    "reminder": "📢 Reminder: Check the latest updates!",
                    "activity": "🎯 Time for some group activity!",
                    "news": "📰 Daily news update is here!"
                }
            }
            self.save_templates()
    
    def save_templates(self):
        """Save templates to file"""
        with open(self.templates_file, 'w') as f:
            json.dump(self.templates, f, indent=2)
    
    def get_template(self, category: str, template_name: str) -> str:
        """Get a specific template"""
        return self.templates.get(category, {}).get(template_name, "")
    
    def add_template(self, category: str, template_name: str, content: str):
        """Add a new template"""
        if category not in self.templates:
            self.templates[category] = {}
        
        self.templates[category][template_name] = content
        self.save_templates()

# Example: Add user analytics
class UserAnalytics:
    """Extension for tracking user analytics"""
    
    def __init__(self):
        self.analytics_file = "analytics.json"
        self.load_analytics()
    
    def load_analytics(self):
        """Load analytics data from file"""
        if os.path.exists(self.analytics_file):
            with open(self.analytics_file, 'r') as f:
                self.analytics = json.load(f)
        else:
            self.analytics = {
                "total_joins": 0,
                "successful_dms": 0,
                "failed_dms": 0,
                "daily_joins": {},
                "user_sources": {}
            }
            self.save_analytics()
    
    def save_analytics(self):
        """Save analytics to file"""
        with open(self.analytics_file, 'w') as f:
            json.dump(self.analytics, f, indent=2)
    
    def record_join(self, user_id: int, username: str, dm_success: bool, source: str = "unknown"):
        """Record a user join"""
        from datetime import datetime
        
        # Update total counts
        self.analytics["total_joins"] += 1
        if dm_success:
            self.analytics["successful_dms"] += 1
        else:
            self.analytics["failed_dms"] += 1
        
        # Update daily stats
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.analytics["daily_joins"]:
            self.analytics["daily_joins"][today] = 0
        self.analytics["daily_joins"][today] += 1
        
        # Update source stats
        if source not in self.analytics["user_sources"]:
            self.analytics["user_sources"][source] = 0
        self.analytics["user_sources"][source] += 1
        
        self.save_analytics()
    
    def get_stats(self) -> dict:
        """Get current analytics stats"""
        return {
            "total_joins": self.analytics["total_joins"],
            "successful_dms": self.analytics["successful_dms"],
            "failed_dms": self.analytics["failed_dms"],
            "success_rate": round(
                (self.analytics["successful_dms"] / max(self.analytics["total_joins"], 1)) * 100, 2
            ),
            "recent_daily_joins": dict(list(self.analytics["daily_joins"].items())[-7:])
        }

# Example: How to integrate these extensions into the main bot
def example_integration():
    """
    Example of how to integrate these extensions into the main bot
    Add this to your bot.py file
    """
    
    # Initialize extensions
    group_targeting = GroupTargetingExtension()
    message_templates = MessageTemplates()
    user_analytics = UserAnalytics()
    
    # Example: Modified send_scheduled_message function
    async def send_scheduled_message_with_targeting():
        """Send scheduled message to specific target groups"""
        active_groups = group_targeting.get_active_groups()
        
        for group in active_groups:
            try:
                # You would need to pass the bot instance here
                # await bot.send_message(
                #     chat_id=group["id"],
                #     text=message_templates.get_template("schedule", "reminder")
                # )
                print(f"Would send message to {group['name']} ({group['id']})")
            except Exception as e:
                print(f"Failed to send message to {group['name']}: {e}")
    
    # Example: Modified handle_join_request function
    async def handle_join_request_with_analytics(update, context):
        """Handle join request with analytics tracking"""
        join_request = update.chat_join_request
        user = join_request.from_user
        chat = join_request.chat
        
        # Approve the request
        await join_request.approve()
        
        # Send welcome message
        dm_success = False
        try:
            # await context.bot.send_message(
            #     chat_id=user.id,
            #     text=message_templates.get_template("welcome", "default")
            # )
            dm_success = True
        except Exception as e:
            print(f"Failed to send DM: {e}")
        
        # Record analytics
        user_analytics.record_join(
            user_id=user.id,
            username=user.username or "Unknown",
            dm_success=dm_success,
            source=chat.type
        )

# Example usage
if __name__ == "__main__":
    print("📚 Example Extensions for Telegram Auto-Join Bot")
    print("=" * 50)
    
    # Initialize extensions
    group_targeting = GroupTargetingExtension()
    message_templates = MessageTemplates()
    user_analytics = UserAnalytics()
    
    # Example: Add a target group
    group_targeting.add_group(-1001234567890, "My Test Group")
    
    # Example: Add a custom template
    message_templates.add_template(
        "welcome", 
        "custom", 
        "Welcome to our amazing community! 🚀\n\nWe're excited to have you here!"
    )
    
    # Example: Get analytics
    stats = user_analytics.get_stats()
    print(f"Total joins: {stats['total_joins']}")
    print(f"Success rate: {stats['success_rate']}%")
    
    print("\n✅ Extensions initialized successfully!")
    print("Copy the relevant code to your bot.py file to use these features.")

