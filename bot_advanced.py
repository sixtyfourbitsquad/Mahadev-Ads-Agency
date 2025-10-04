#!/usr/bin/env python3
"""
VipPlay247 Telegram Bot - Advanced Join Request Management
Features:
- Batch approval of join requests with /accept command
- Automatically sends welcome message after approval
- VipPlay247 branded welcome message with buttons
- Admin panel for configuration
- File-based configuration (no database)
"""

import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters, ChatJoinRequestHandler, ChatMemberHandler
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class VipPlay247Bot:
    def __init__(self, token: str):
        self.token = token
        # Enable chat member updates
        self.application = Application.builder().token(token).build()
        
        # Store channel IDs where bot is admin
        self.monitored_channels = set()
        
        # Configuration files
        self.WELCOME_FILE = "welcome.txt"
        self.ADMINS_FILE = "admins.json"
        self.LOGS_FILE = "logs.txt"
        self.CONFIG_FILE = "bot_config.json"
        self.USERS_FILE = "users.json"
        
        # Bot configuration
        self.bot_config = {
            "welcome_image": "",
            "welcome_text": "Welcome to VipPlay247! 🎉",
            "signup_url": "",
            "join_group_url": "",
            "download_apk": "",
            "daily_bonuses_url": "",
            "admin_group_id": "",
            "live_chat_enabled": False
        }
        
        # Broadcast configuration
        self.broadcast_file = "broadcast_data.json"
        
        # Admin states for configuration
        self.admin_states = {}  # Track admin conversation states
        
        # Store pending join requests
        self.pending_requests = []  # List of {chat_id, user_id, user_data, timestamp}
        
        # Load configuration
        self.load_config()
        
        # Setup handlers
        self.setup_handlers()
        
    def load_config(self):
        """Load configuration from files"""
        # Load admins
        try:
            with open(self.ADMINS_FILE, 'r') as f:
                self.admins = json.load(f)
        except FileNotFoundError:
            self.admins = [5638736363]  # Default admin
            self.save_admins()
            
        # Load bot configuration
        try:
            with open(self.CONFIG_FILE, 'r') as f:
                self.bot_config.update(json.load(f))
        except FileNotFoundError:
            self.save_bot_config()
            
        # Load welcome message
        try:
            with open(self.WELCOME_FILE, 'r') as f:
                self.bot_config["welcome_text"] = f.read().strip()
        except FileNotFoundError:
            self.save_welcome()
            
        # Load users
        try:
            with open(self.USERS_FILE, 'r') as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = {}
            self.save_users()
            
    def save_bot_config(self):
        """Save bot configuration to file"""
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(self.bot_config, f, indent=2)
            
    def save_admins(self):
        """Save admin list to file"""
        with open(self.ADMINS_FILE, 'w') as f:
            json.dump(self.admins, f)
            
    def save_welcome(self):
        """Save welcome message to file"""
        with open(self.WELCOME_FILE, 'w', encoding='utf-8') as f:
            f.write(self.bot_config["welcome_text"])
            
    def save_users(self):
        """Save users to file"""
        with open(self.USERS_FILE, 'w') as f:
            json.dump(self.users, f, indent=2)
            
    def log_join(self, username: str, user_id: int, dm_sent: bool, error: str = None):
        """Log join request details"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "✅ DM Sent" if dm_sent else "❌ DM Failed"
        error_info = f" (Error: {error})" if error else ""
        
        log_entry = f"[{timestamp}] @{username} (ID: {user_id}) - {status}{error_info}\n"
        
        with open(self.LOGS_FILE, 'a') as f:
            f.write(log_entry)
            
    def setup_handlers(self):
        """Setup message handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("id", self.show_chat_id))
        self.application.add_handler(CommandHandler("welcome", self.manual_welcome_command))
        self.application.add_handler(CommandHandler("pending", self.show_pending_users))
        self.application.add_handler(CommandHandler("accept", self.accept_requests_command))
        
        # Callback query handler for inline buttons
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Message handler for admin responses
        self.application.add_handler(MessageHandler(
            (filters.TEXT | filters.VOICE | filters.PHOTO | filters.VIDEO | 
             filters.Document.ALL | filters.AUDIO | filters.VIDEO_NOTE | 
             filters.Sticker.ALL | filters.ANIMATION) & ~filters.COMMAND, 
            self.handle_message
        ))
        
        # Join request handler (no longer auto-accepts)
        self.application.add_handler(ChatJoinRequestHandler(self.handle_join_request))
        
        # Chat member handler to detect when admin approves join requests
        self.application.add_handler(ChatMemberHandler(self.handle_chat_member_update, ChatMemberHandler.CHAT_MEMBER))
        
        # Also add handler for MY_CHAT_MEMBER to catch when bot is added/removed
        self.application.add_handler(ChatMemberHandler(self.handle_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Store user information (but not admin users)
        if str(user.id) not in self.users and user.id not in self.admins:
            self.users[str(user.id)] = {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "joined_date": datetime.now().isoformat()
            }
            self.save_users()
        
        # Send the same welcome message that users get when joining channels
        await self.send_welcome_message(context.bot, user.id)
        
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command - show admin panel"""
        user_id = update.effective_user.id
        
        if user_id not in self.admins:
            await update.message.reply_text("❌ Access denied. You are not authorized as an admin.")
            return
            
        await self.show_admin_panel(update, context)
        
    async def manual_welcome_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /welcome command - manually send welcome to user"""
        user_id = update.effective_user.id
        
        if user_id not in self.admins:
            await update.message.reply_text("❌ Access denied. Only admins can use this command.")
            return
            
        # Check if this is a reply to a message
        if update.message.reply_to_message:
            target_user_id = update.message.reply_to_message.from_user.id
            target_username = update.message.reply_to_message.from_user.username
            
            try:
                # Send welcome message to the target user
                await self.send_welcome_message(context.bot, target_user_id)
                await update.message.reply_text(f"✅ Welcome message sent to @{target_username} (ID: {target_user_id})")
                self.log_join(target_username, target_user_id, True, "Manual welcome by admin")
                
            except Exception as e:
                await update.message.reply_text(f"❌ Failed to send welcome message: {str(e)}")
                logger.error(f"Failed to send manual welcome: {e}")
        else:
            await update.message.reply_text(
                "ℹ️ **How to use /welcome command:**\n\n"
                "Reply to a user's message with `/welcome` to send them the welcome message.\n\n"
                "**Example:**\n"
                "1. Find a message from the user you want to welcome\n"
                "2. Reply to that message with `/welcome`\n"
                "3. Bot will send the welcome message to that user"
            )
        
    async def show_pending_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show users pending approval and allow manual welcome"""
        user_id = update.effective_user.id
        
        if user_id not in self.admins:
            await update.message.reply_text("❌ Access denied. Only admins can use this command.")
            return
            
        # Find pending users
        pending_users = []
        for uid, user_data in self.users.items():
            if user_data.get('pending_approval', False):
                username = user_data.get('username', 'No username')
                first_name = user_data.get('first_name', 'Unknown')
                joined_date = user_data.get('joined_date', 'Unknown')
                pending_users.append(f"• @{username} ({first_name}) - ID: {uid}\n  Requested: {joined_date[:10]}")
        
        if not pending_users:
            await update.message.reply_text(
                "✅ **No Pending Users**\n\n"
                "All users have been processed!\n\n"
                "**Commands:**\n"
                "• `/welcome` - Reply to a user's message to send welcome\n"
                "• `/pending` - Check this list again"
            )
        else:
            message = f"⏳ **Users Pending Approval ({len(pending_users)}):**\n\n"
            message += "\n\n".join(pending_users)
            message += "\n\n**To send welcome message:**\n"
            message += "1. Approve the user in your channel\n"
            message += "2. Use `/welcome` command by replying to their message\n"
            message += "3. Or wait for automatic detection (if working)"
            
            await update.message.reply_text(message)
        
    async def accept_requests_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /accept command - Accept specified number of join requests"""
        user_id = update.effective_user.id
        
        if user_id not in self.admins:
            await update.message.reply_text("❌ Access denied. Only admins can use this command.")
            return
            
        # Get the number from command arguments
        try:
            args = context.args
            if not args:
                await update.message.reply_text(
                    "ℹ️ **How to use /accept command:**\n\n"
                    f"**Current pending requests:** {len(self.pending_requests)}\n\n"
                    "**Usage:**\n"
                    "• `/accept 5` - Accept 5 join requests\n"
                    "• `/accept all` - Accept all pending requests\n"
                    "• `/accept 0` - Show pending count without accepting\n\n"
                    "**Examples:**\n"
                    "• `/accept 3` - Accepts 3 oldest requests\n"
                    "• `/accept all` - Accepts all requests"
                )
                return
                
            if args[0].lower() == 'all':
                num_to_accept = len(self.pending_requests)
            else:
                num_to_accept = int(args[0])
                
            if num_to_accept < 0:
                await update.message.reply_text("❌ Number must be positive!")
                return
                
            if num_to_accept == 0:
                await update.message.reply_text(f"ℹ️ **Current Status:**\n\nPending requests: {len(self.pending_requests)}")
                return
                
        except ValueError:
            await update.message.reply_text("❌ Invalid number! Use `/accept 5` or `/accept all`")
            return
            
        # Check if there are requests to process
        if not self.pending_requests:
            await update.message.reply_text("✅ No pending join requests to accept!")
            return
            
        # Limit to available requests
        num_to_accept = min(num_to_accept, len(self.pending_requests))
        
        await update.message.reply_text(f"🔄 Processing {num_to_accept} join requests...")
        
        # Process the requests
        accepted = 0
        failed = 0
        
        for i in range(num_to_accept):
            if not self.pending_requests:
                break
                
            request = self.pending_requests.pop(0)  # Get oldest request
            
            try:
                # Approve the join request
                await context.bot.approve_chat_join_request(
                    chat_id=request["chat_id"],
                    user_id=request["user_id"]
                )
                
                # Send welcome message
                await self.send_welcome_message(context.bot, request["user_id"])
                
                # Update user status
                if str(request["user_id"]) in self.users:
                    self.users[str(request["user_id"])]["pending_approval"] = False
                    self.users[str(request["user_id"])]["approved_date"] = datetime.now().isoformat()
                
                # Log success
                self.log_join(request["username"], request["user_id"], True, "Batch approved by admin")
                accepted += 1
                
                logger.info(f"Approved and welcomed: {request['username']} (ID: {request['user_id']})")
                
            except Exception as e:
                logger.error(f"Failed to process request for {request['username']}: {e}")
                self.log_join(request["username"], request["user_id"], False, f"Batch approval failed: {str(e)}")
                failed += 1
                
        # Save updated user data
        self.save_users()
        
        # Send summary
        summary = f"✅ **Batch Processing Complete!**\n\n"
        summary += f"✅ **Accepted:** {accepted}\n"
        summary += f"❌ **Failed:** {failed}\n"
        summary += f"⏳ **Remaining pending:** {len(self.pending_requests)}"
        
        await update.message.reply_text(summary)
        
    async def show_chat_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /id command - show chat ID for channels and groups"""
        chat = update.effective_chat
        
        # Only work in channels and groups
        if chat.type not in ['channel', 'supergroup', 'group']:
            await update.message.reply_text(
                "❌ **Error**\n\n"
                "This command only works in channels and groups.\n"
                "Use this command in the channel/group where you want to get the ID."
            )
            return
            
        # Check if user is admin in the chat
        try:
            member = await context.bot.get_chat_member(chat.id, update.effective_user.id)
            if member.status not in ['creator', 'administrator']:
                await update.message.reply_text(
                    "❌ **Access Denied**\n\n"
                    "You need to be an admin in this channel/group to use this command."
                )
                return
        except Exception as e:
            await update.message.reply_text(
                "❌ **Error**\n\n"
                "Could not verify your admin status. Make sure the bot has admin rights."
            )
            return
            
        # Show chat information
        chat_type = "Channel" if chat.type == "channel" else "Supergroup" if chat.type == "supergroup" else "Group"
        username_info = f"\n**Username:** @{chat.username}" if chat.username else "\n**Username:** None (Private)"
        
        await update.message.reply_text(
            f"📋 **Chat Information**\n\n"
            f"**Type:** {chat_type}\n"
            f"**Title:** {chat.title}\n"
            f"**ID:** `{chat.id}`\n"
            f"{username_info}\n\n"
            f"**To set as admin group:**\n"
            f"1. Copy the ID: `{chat.id}`\n"
            f"2. Send `/admin` to your bot\n"
            f"3. Click '⚙️ Bot Configuration'\n"
            f"4. Click '📱 Set Admin Group'",
            parse_mode='Markdown'
        )
        
    async def show_admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show the admin panel with inline buttons"""
        keyboard = [
            [
                InlineKeyboardButton("📝 Set Welcome Text", callback_data="set_welcome_text"),
                InlineKeyboardButton("🖼️ Set Welcome Image", callback_data="set_welcome_image")
            ],
            [
                InlineKeyboardButton("🆔 Set Get ID URL", callback_data="set_signup_url"),
                InlineKeyboardButton("📹 Set Guide Video URL", callback_data="set_join_group_url")
            ],
            [
                InlineKeyboardButton("📱 Set Telegram URL", callback_data="set_download_apk"),
                InlineKeyboardButton("📸 Set Instagram URL", callback_data="set_daily_bonuses")
            ],
            [
                InlineKeyboardButton("📱 Set Admin Group", callback_data="set_admin_group"),
                InlineKeyboardButton("⚙️ Bot Configuration", callback_data="bot_config")
            ],
            [
                InlineKeyboardButton("📡 Send Message to All Users", callback_data="send_broadcast"),
                InlineKeyboardButton("👥 View User Stats", callback_data="view_users")
            ],
            [
                InlineKeyboardButton("📑 View Logs", callback_data="view_logs"),
                InlineKeyboardButton("🛑 Stop Bot", callback_data="stop_bot")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🔧 **Advanced Admin Panel**\n\n"
            "Welcome to the admin panel. Use the buttons below to configure the bot:",
            reply_markup=reply_markup
        )
        
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline buttons"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        # Handle user buttons first (these work for everyone)
        if data == "signup":
            await self.handle_get_id(query, context)
            return
            
        elif data == "join_group":
            await self.handle_guide_video(query, context)
            return
            
            
        elif data == "download_hack":
            await self.handle_telegram_join(query, context)
            return
            
        elif data == "daily_bonuses":
            await self.handle_instagram_join(query, context)
            return
            
        
        # Admin-only buttons below
        if user_id not in self.admins:
            await query.edit_message_text("❌ Access denied. You are not authorized as an admin.")
            return
            
        if data == "set_welcome_text":
            self.admin_states[user_id] = "waiting_welcome_text"
            await query.edit_message_text(
                "📝 **Set Welcome Text**\n\n"
                "Send the new welcome message text. This will be displayed with the welcome image."
            )
            
        elif data == "set_welcome_image":
            self.admin_states[user_id] = "waiting_welcome_image"
            await query.edit_message_text(
                "🖼️ **Set Welcome Image**\n\n"
                "Send the image you want to use as the welcome image."
            )
            
        elif data == "set_signup_url":
            self.admin_states[user_id] = "waiting_signup_url"
            await query.edit_message_text(
                "🆔 **Set Get ID URL**\n\n"
                "Send the URL for the 'Get ID Now' button (e.g., https://vipplay247.com/register)"
            )
            
        elif data == "set_join_group_url":
            self.admin_states[user_id] = "waiting_join_group_url"
            await query.edit_message_text(
                "📹 **Set Guide Video URL**\n\n"
                "Send the URL for the VipPlay247 Full Guide Video (e.g., https://youtube.com/watch?v=...)"
            )
            
        elif data == "set_download_apk":
            self.admin_states[user_id] = "waiting_download_apk"
            await query.edit_message_text(
                "📱 **Set Telegram URL**\n\n"
                "Send the Telegram link for VipPlay247 (e.g., https://t.me/vipplay247)"
            )
            
        elif data == "set_daily_bonuses":
            self.admin_states[user_id] = "waiting_daily_bonuses"
            await query.edit_message_text(
                "📸 **Set Instagram URL**\n\n"
                "Send the Instagram URL for VipPlay247 (e.g., https://instagram.com/vipplay247)"
            )
            
        elif data == "set_admin_group":
            self.admin_states[user_id] = "waiting_admin_group"
            await query.edit_message_text(
                "📱 **Set Admin Group**\n\n"
                "Send the group ID where admin replies should be sent.\n\n"
                "Use /id command in the target group to get the ID."
            )
            
        elif data == "bot_config":
            await self.show_bot_config(query)
            
        elif data == "send_broadcast":
            self.admin_states[user_id] = "waiting_broadcast"
            await query.edit_message_text(
                "📡 **Send Message to All Users**\n\n"
                "Send the message you want to broadcast to all users.\n\n"
                "**Supported formats:**\n"
                "• 📝 Text message\n"
                "• 🖼️ Image with caption\n"
                "• 🎥 Video with caption\n"
                "• 🎵 Audio with caption\n"
                "• 📄 Document with caption\n"
                "• 🎙️ Voice message\n"
                "• 🎭 Sticker\n"
                "• 🎬 GIF/Animation\n\n"
                "Send your message now..."
            )
            
        elif data == "view_users":
            await self.show_user_stats(query)
            
        elif data == "view_logs":
            await self.show_logs(query)
            
        elif data == "stop_bot":
            await self.stop_bot(query)
            
        elif data == "back_to_admin":
            await self.show_admin_panel_from_query(query, context)
            
    async def show_bot_config(self, query):
        """Show current bot configuration"""
        config_text = f"""
🔧 **Bot Configuration**

📝 **Welcome Text:** {self.bot_config['welcome_text'][:50]}{'...' if len(self.bot_config['welcome_text']) > 50 else ''}
🖼️ **Welcome Image:** {'✅ Set' if self.bot_config['welcome_image'] else '❌ Not Set'}
🆔 **Get ID URL:** {self.bot_config['signup_url'] or '❌ Not Set'}
📹 **Guide Video URL:** {self.bot_config['join_group_url'] or '❌ Not Set'}
📱 **Telegram URL:** {self.bot_config['download_apk'] or '❌ Not Set'}
📸 **Instagram URL:** {self.bot_config['daily_bonuses_url'] or '❌ Not Set'}
📱 **Admin Group ID:** {self.bot_config['admin_group_id'] or '❌ Not Set'}
        """.strip()
        
        keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(config_text, reply_markup=reply_markup)
        
    async def show_user_stats(self, query):
        """Show user statistics"""
        total_users = len(self.users)
        recent_users = sum(1 for user in self.users.values() 
                         if (datetime.now() - datetime.fromisoformat(user["joined_date"])).days <= 7)
        
        await query.edit_message_text(
            f"👥 **User Statistics**\n\n"
            f"📊 **Total Users:** {total_users}\n"
            f"🆕 **New Users (7 days):** {recent_users}\n\n"
            f"**User Breakdown:**\n"
            f"• Users with username: {sum(1 for u in self.users.values() if u.get('username'))}\n"
            f"• Users without username: {sum(1 for u in self.users.values() if not u.get('username'))}\n\n"
            f"**Recent Users:**\n" + 
            "\n".join([f"• @{u['username'] or 'No username'} ({u['first_name']})" 
                       for u in list(self.users.values())[-5:]]) if self.users else "No users yet",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin")
            ]])
        )
        
    async def show_logs(self, query):
        """Show recent logs"""
        try:
            with open(self.LOGS_FILE, 'r') as f:
                logs = f.readlines()
                
            if not logs:
                await query.edit_message_text(
                    "📑 **No Logs Available**\n\n"
                    "No activity has been logged yet.",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin")
                    ]])
                )
                return
                
            # Show last 10 log entries
            recent_logs = logs[-10:]
            log_text = "📑 **Recent Activity Logs**\n\n" + "".join(recent_logs)
            
            # Truncate if too long
            if len(log_text) > 4000:
                log_text = log_text[:4000] + "\n\n... (truncated)"
                
            await query.edit_message_text(
                log_text,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin")
                ]])
            )
            
        except Exception as e:
            await query.edit_message_text(
                f"❌ **Error Reading Logs**\n\n{str(e)}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin")
                ]])
            )
            
    async def stop_bot(self, query):
        """Stop the bot"""
        await query.edit_message_text(
            "🛑 **Bot Stopped**\n\n"
            "The bot has been stopped. You can restart it by running the script again.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin")
            ]])
        )
        
    async def show_admin_panel_from_query(self, query, context):
        """Show admin panel from callback query"""
        await self.show_admin_panel(update=query, context=context)
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages for admin responses"""
        user_id = update.effective_user.id
        message = update.message
        
        # Check if user is waiting for a response (admin)
        if user_id in self.admin_states:
            state = self.admin_states[user_id]
            await self.handle_admin_response(update, context, state)
            return
            
    async def handle_admin_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE, state: str):
        """Handle admin responses for configuration"""
        message = update.message
        user_id = update.effective_user.id
        
        if state == "waiting_welcome_text":
            self.bot_config["welcome_text"] = message.text
            self.save_welcome()
            await message.reply_text("✅ Welcome text updated successfully!")
            
        elif state == "waiting_welcome_image":
            if message.photo:
                file_id = message.photo[-1].file_id
                self.bot_config["welcome_image"] = file_id
                self.save_bot_config()
                await message.reply_text("✅ Welcome image updated successfully!")
            else:
                await message.reply_text("❌ Please send an image file.")
                return
                
        elif state == "waiting_signup_url":
            if message.text and message.text.startswith(('http://', 'https://')):
                self.bot_config["signup_url"] = message.text
                self.save_bot_config()
                await message.reply_text("✅ Signup URL updated successfully!")
            else:
                await message.reply_text("❌ Please send a valid URL starting with http:// or https://")
                return
                
        elif state == "waiting_join_group_url":
            if message.text and message.text.startswith(('http://', 'https://')):
                self.bot_config["join_group_url"] = message.text
                self.save_bot_config()
                await message.reply_text("✅ Guide Video URL updated successfully!")
            else:
                await message.reply_text("❌ Please send a valid URL starting with http:// or https://")
                return
                
        elif state == "waiting_download_apk":
            if message.text and message.text.startswith(('http://', 'https://')):
                self.bot_config["download_apk"] = message.text
                self.save_bot_config()
                await message.reply_text("✅ Telegram URL updated successfully!")
            elif message.document:
                file_id = message.document.file_id
                self.bot_config["download_apk"] = file_id
                self.save_bot_config()
                await message.reply_text("✅ Telegram content file updated successfully!")
            else:
                await message.reply_text("❌ Please send a valid URL starting with http:// or https://")
                return
                
        elif state == "waiting_daily_bonuses":
            if message.text and message.text.startswith(('http://', 'https://')):
                self.bot_config["daily_bonuses_url"] = message.text
                self.save_bot_config()
                await message.reply_text("✅ Daily bonuses URL updated successfully!")
            else:
                await message.reply_text("❌ Please send a valid URL starting with http:// or https://")
                return
                
        elif state == "waiting_admin_group":
            try:
                group_id = int(message.text)
                self.bot_config["admin_group_id"] = str(group_id)
                self.save_bot_config()
                await message.reply_text(f"✅ Admin group ID updated to: {group_id}")
            except ValueError:
                await message.reply_text("❌ Please send a valid group ID (numbers only)")
                return
                
        elif state == "waiting_broadcast":
            await self.broadcast_message_to_all_users(message, context)
            return
            
        # Clear admin state
        if user_id in self.admin_states:
            del self.admin_states[user_id]
            
            
            
    async def broadcast_message_to_all_users(self, message, context):
        """Send message to all users (BROADCAST FEATURE)"""
        if not self.users:
            await message.reply_text("❌ No users found to broadcast to.")
            return

        # Save broadcast message data
        message_data = {}
        if message.text:
            message_data = {"type": "text", "content": message.text}
        elif message.photo:
            message_data = {"type": "photo", "file_id": message.photo[-1].file_id, "caption": message.caption}
        elif message.video:
            message_data = {"type": "video", "file_id": message.video.file_id, "caption": message.caption}
        elif message.voice:
            message_data = {"type": "voice", "file_id": message.voice.file_id, "caption": message.caption}
        elif message.audio:
            message_data = {"type": "audio", "file_id": message.audio.file_id, "caption": message.caption}
        elif message.document:
            message_data = {"type": "document", "file_id": message.document.file_id, "caption": message.caption}
        elif message.video_note:
            message_data = {"type": "video_note", "file_id": message.video_note.file_id}
        elif message.sticker:
            message_data = {"type": "sticker", "file_id": message.sticker.file_id}
        elif message.animation:
            message_data = {"type": "animation", "file_id": message.animation.file_id, "caption": message.caption}
        else:
            await message.reply_text("❌ Unsupported message type for broadcast.")
            return

        # Save broadcast data
        with open(self.broadcast_file, 'w', encoding='utf-8') as f:
            json.dump(message_data, f, indent=2, ensure_ascii=False)

        # Send to all users
        success_count = 0
        failed_count = 0

        await message.reply_text(f"📡 Broadcasting message to {len(self.users)} users...")

        for user_id, user_info in self.users.items():
            # Skip admin users
            if int(user_id) in self.admins:
                continue

            try:
                if message_data["type"] == "text":
                    await context.bot.send_message(
                        chat_id=int(user_id),
                        text=message_data["content"]
                    )
                elif message_data["type"] == "photo":
                    await context.bot.send_photo(
                        chat_id=int(user_id),
                        photo=message_data["file_id"],
                        caption=message_data.get("caption")
                    )
                elif message_data["type"] == "video":
                    await context.bot.send_video(
                        chat_id=int(user_id),
                        video=message_data["file_id"],
                        caption=message_data.get("caption")
                    )
                elif message_data["type"] == "voice":
                    await context.bot.send_voice(
                        chat_id=int(user_id),
                        voice=message_data["file_id"],
                        caption=message_data.get("caption")
                    )
                elif message_data["type"] == "audio":
                    await context.bot.send_audio(
                        chat_id=int(user_id),
                        audio=message_data["file_id"],
                        caption=message_data.get("caption")
                    )
                elif message_data["type"] == "document":
                    await context.bot.send_document(
                        chat_id=int(user_id),
                        document=message_data["file_id"],
                        caption=message_data.get("caption")
                    )
                elif message_data["type"] == "video_note":
                    await context.bot.send_video_note(
                        chat_id=int(user_id),
                        video_note=message_data["file_id"]
                    )
                elif message_data["type"] == "sticker":
                    await context.bot.send_sticker(
                        chat_id=int(user_id),
                        sticker=message_data["file_id"]
                    )
                elif message_data["type"] == "animation":
                    await context.bot.send_animation(
                        chat_id=int(user_id),
                        animation=message_data["file_id"],
                        caption=message_data.get("caption")
                    )

                success_count += 1
                time.sleep(0.1)  # Small delay to avoid rate limiting

            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send broadcast to user {user_id}: {e}")

        # Send summary
        await message.reply_text(
            f"📡 **Broadcast Complete!**\n\n"
            f"✅ Successfully sent: {success_count}\n"
            f"❌ Failed: {failed_count}\n"
            f"📊 Total users: {len(self.users)}"
        )

        # Log the broadcast
        self.log_broadcast(success_count, failed_count, len(self.users))
        
    def log_broadcast(self, success_count, failed_count, total_users):
        """Log broadcast activity"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] BROADCAST - Success: {success_count}, Failed: {failed_count}, Total: {total_users}\n"
        
        with open(self.LOGS_FILE, 'a') as f:
            f.write(log_entry)
            
    async def handle_join_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle join requests - Store them for batch approval"""
        join_request = update.chat_join_request
        
        try:
            # Log the join request
            logger.info(f"Join request received from {join_request.from_user.username} (ID: {join_request.from_user.id})")
            
            # Store the join request for batch processing
            request_data = {
                "chat_id": join_request.chat.id,
                "user_id": join_request.from_user.id,
                "username": join_request.from_user.username,
                "first_name": join_request.from_user.first_name,
                "last_name": join_request.from_user.last_name,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add to pending requests list
            self.pending_requests.append(request_data)
            
            # Also store in users database
            if str(join_request.from_user.id) not in self.users and join_request.from_user.id not in self.admins:
                self.users[str(join_request.from_user.id)] = {
                    "username": join_request.from_user.username,
                    "first_name": join_request.from_user.first_name,
                    "last_name": join_request.from_user.last_name,
                    "joined_date": datetime.now().isoformat(),
                    "pending_approval": True
                }
                self.save_users()
            
            # Log the pending request
            self.log_join(join_request.from_user.username, join_request.from_user.id, False, f"Stored for batch approval ({len(self.pending_requests)} pending)")
            
            logger.info(f"Total pending requests: {len(self.pending_requests)}")
            
        except Exception as e:
            logger.error(f"Error handling join request: {e}")
            self.log_join(join_request.from_user.username, join_request.from_user.id, False, str(e))
            
    async def handle_chat_member_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle chat member updates - detect when admin approves join requests"""
        try:
            chat_member_update = update.chat_member
            
            logger.info(f"Chat member update detected: {chat_member_update.old_chat_member.status} -> {chat_member_update.new_chat_member.status}")
            
            # Check if this is a status change from 'left' to 'member' (approved join request)
            if (chat_member_update.old_chat_member.status == 'left' and 
                chat_member_update.new_chat_member.status == 'member'):
                
                user = chat_member_update.new_chat_member.user
                logger.info(f"User {user.username} (ID: {user.id}) was approved by admin")
                
                # Check if this user was pending approval
                user_data = self.users.get(str(user.id), {})
                if user_data.get('pending_approval', False):
                    # Remove pending approval flag
                    user_data['pending_approval'] = False
                    user_data['approved_date'] = datetime.now().isoformat()
                    self.users[str(user.id)] = user_data
                    self.save_users()
                    
                    # Send welcome message automatically
                    await self.send_welcome_message(context.bot, user.id)
                    self.log_join(user.username, user.id, True, "Auto-sent after admin approval")
                    
                    logger.info(f"Welcome message sent to {user.username} (ID: {user.id}) after admin approval")
                else:
                    # User wasn't pending, but still send welcome message
                    logger.info(f"User {user.username} joined but wasn't in pending list, sending welcome anyway")
                    await self.send_welcome_message(context.bot, user.id)
                    self.log_join(user.username, user.id, True, "Welcome sent to new member")
                
        except Exception as e:
            logger.error(f"Error handling chat member update: {e}")
            
    async def handle_my_chat_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle updates about the bot's own chat member status"""
        try:
            my_chat_member = update.my_chat_member
            logger.info(f"Bot status update: {my_chat_member.old_chat_member.status} -> {my_chat_member.new_chat_member.status}")
            
            if my_chat_member.new_chat_member.status == 'administrator':
                logger.info(f"Bot was made admin in chat {my_chat_member.chat.title}")
            elif my_chat_member.new_chat_member.status == 'member':
                logger.info(f"Bot was added as member to chat {my_chat_member.chat.title}")
                
        except Exception as e:
            logger.error(f"Error handling my chat member update: {e}")
            
    async def send_welcome_message(self, bot, user_id: int):
        """Send welcome message with image and buttons"""
        try:
            # Create inline keyboard - each button on its own row (full width)
            keyboard = []
            
            if self.bot_config["signup_url"]:
                keyboard.append([InlineKeyboardButton("🆔 Get ID Now", url=self.bot_config["signup_url"])])
                
            if self.bot_config["join_group_url"]:
                keyboard.append([InlineKeyboardButton("📹 VipPlay247 Full Guide Video", url=self.bot_config["join_group_url"])])
                
            if self.bot_config["download_apk"]:
                # If it's a URL, make it a URL button, otherwise callback
                if self.bot_config["download_apk"].startswith(('http://', 'https://')):
                    keyboard.append([InlineKeyboardButton("📱 Join VipPlay247 Telegram", url=self.bot_config["download_apk"])])
                else:
                    keyboard.append([InlineKeyboardButton("📱 Join VipPlay247 Telegram", callback_data="download_hack")])
                
            if self.bot_config["daily_bonuses_url"]:
                keyboard.append([InlineKeyboardButton("📸 Join VipPlay247 Instagram", url=self.bot_config["daily_bonuses_url"])])
                
            reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
            
            # Send welcome message
            if self.bot_config["welcome_image"]:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=self.bot_config["welcome_image"],
                    caption=self.bot_config["welcome_text"],
                    reply_markup=reply_markup
                )
            else:
                await bot.send_message(
                    chat_id=user_id,
                    text=self.bot_config["welcome_text"],
                    reply_markup=reply_markup
                )
                
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")
            # Fallback to text-only message
            try:
                await bot.send_message(
                    chat_id=user_id,
                    text=self.bot_config["welcome_text"]
                )
            except Exception as e2:
                logger.error(f"Failed to send fallback welcome message: {e2}")
                
    # Button handlers
    async def handle_get_id(self, query, context):
        """Handle Get ID Now button click"""
        if self.bot_config["signup_url"]:
            await query.answer("🆔 **Get your VipPlay247 ID now!** 🚀")
            # The button already has the URL, so no action needed
        else:
            await query.answer("❌ Get ID URL not configured yet!", show_alert=True)
            
    async def handle_guide_video(self, query, context):
        """Handle VipPlay247 Full Guide Video button click"""
        if self.bot_config["join_group_url"]:
            await query.answer("📹 **Watch the complete guide!** 🎥")
            # The button already has the URL, so no action needed
        else:
            await query.answer("❌ Guide video URL not configured yet!", show_alert=True)
            
            
    async def handle_telegram_join(self, query, context):
        """Handle Join VipPlay247 Telegram button click"""
        try:
            if self.bot_config["download_apk"]:
                # If download_apk contains a URL, treat it as Telegram link
                if self.bot_config["download_apk"].startswith(('http://', 'https://')):
                    await query.answer("📱 **Join VipPlay247 Telegram!** 🚀")
                    # This should be handled as URL button, but keeping for compatibility
                else:
                    # If it's a file ID, send the file
                    await context.bot.send_document(
                        chat_id=query.from_user.id,
                        document=self.bot_config["download_apk"],
                        caption="📱 **VipPlay247 Telegram Content!** 📱\n\n🔥 **Join us now!** 🔥"
                    )
                    await query.answer("📱 Content delivered! Join our Telegram! 🚀")
            else:
                await query.answer("❌ Telegram link not configured yet!", show_alert=True)

        except Exception as e:
            logger.error(f"Failed to handle Telegram join: {e}")
            await query.answer("❌ Failed to process request", show_alert=True)
            
    async def handle_instagram_join(self, query, context):
        """Handle Join VipPlay247 Instagram button click"""
        if self.bot_config["daily_bonuses_url"]:
            await query.answer("📸 **Follow VipPlay247 on Instagram!** ⭐")
            # The button already has the URL, so no action needed
        else:
            await query.answer("❌ Instagram URL not configured yet!", show_alert=True)
            
    def run(self):
        """Run the bot"""
        print("🚀 Starting VipPlay247 Bot...")
        self.application.run_polling()

def main():
    """Main function"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        print("Please set your bot token:")
        print("export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return
        
    bot = VipPlay247Bot(token)
    bot.run()

if __name__ == "__main__":
    main()
