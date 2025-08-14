#!/usr/bin/env python3
"""
Telegram Bot with Auto-Join Request Approval, Welcome Messages, and Admin Panel
Features:
- Auto-accept join requests
- Send welcome DM to new members
- Admin panel with inline buttons
- Send message to all users (NEW FEATURE)
- File-based configuration (no database)
"""

import json
import logging
import os
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
    ContextTypes, filters, ChatJoinRequestHandler
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        
        # Configuration files
        self.WELCOME_FILE = "welcome.txt"
        self.ADMINS_FILE = "admins.json"
        self.LOGS_FILE = "logs.txt"
        self.CHANNELS_FILE = "channels.json"
        self.USERS_FILE = "users.json"  # NEW: Store all users
        
        # Message data storage
        self.welcome_message_data = None
        self.users = {}  # NEW: Store user information
        
        # Admin states for handling responses
        self.admin_states = {}
        
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
            
        # Load channels
        try:
            with open(self.CHANNELS_FILE, 'r') as f:
                self.channels = json.load(f)
        except FileNotFoundError:
            self.channels = {}
            self.save_channels()
            
        # Load welcome message
        try:
            with open(self.WELCOME_FILE, 'r') as f:
                self.welcome_message = f.read().strip()
        except FileNotFoundError:
            self.welcome_message = "Welcome to our group! 🎉\n\nWe're glad to have you here. Please read the rules and enjoy your stay!"
            self.save_welcome()
            
        # Load users (NEW)
        try:
            with open(self.USERS_FILE, 'r') as f:
                self.users = json.load(f)
        except FileNotFoundError:
            self.users = {}
            self.save_users()
            
        # Load message data
        self.welcome_message_data = self.load_message_data("welcome")
        
    def load_message_data(self, message_type: str):
        """Load message data from JSON file"""
        filename = f"{message_type}_data.json"
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None
        
    def save_welcome_data(self):
        """Save welcome message data to JSON file"""
        if self.welcome_message_data:
            with open("welcome_data.json", 'w', encoding='utf-8') as f:
                json.dump(self.welcome_message_data, f, indent=2, ensure_ascii=False)
                
    def save_channels(self):
        """Save channels to file"""
        with open(self.CHANNELS_FILE, 'w') as f:
            json.dump(self.channels, f, indent=2)
                
    def save_admins(self):
        """Save admin list to file"""
        with open(self.ADMINS_FILE, 'w') as f:
            json.dump(self.admins, f)
            
    def save_welcome(self):
        """Save welcome message to file"""
        with open(self.WELCOME_FILE, 'w', encoding='utf-8') as f:
            f.write(self.welcome_message)
            
    def save_users(self):
        """Save users to file (NEW)"""
        with open(self.USERS_FILE, 'w') as f:
            json.dump(self.users, f, indent=2)
            
    async def save_message_by_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_type: str):
        """Save message based on its type (text, photo, video, voice, etc.)"""
        message = update.message
        
        # Create message data structure
        message_data = {
            "type": None,
            "content": None,
            "file_id": None,
            "caption": None
        }
        
        if message.text:
            message_data["type"] = "text"
            message_data["content"] = message.text
        elif message.voice:
            message_data["type"] = "voice"
            message_data["file_id"] = message.voice.file_id
            message_data["caption"] = message.caption
        elif message.photo:
            message_data["type"] = "photo"
            message_data["file_id"] = message.photo[-1].file_id
            message_data["caption"] = message.caption
        elif message.video:
            message_data["type"] = "video"
            message_data["file_id"] = message.video.file_id
            message_data["caption"] = message.caption
        elif message.audio:
            message_data["type"] = "audio"
            message_data["file_id"] = message.audio.file_id
            message_data["caption"] = message.caption
        elif message.document:
            message_data["type"] = "document"
            message_data["file_id"] = message.document.file_id
            message_data["caption"] = message.caption
        elif message.video_note:
            message_data["type"] = "video_note"
            message_data["file_id"] = message.video_note.file_id
            message_data["caption"] = message.caption
            
        # Save based on message type
        if message_type == "welcome":
            self.welcome_message_data = message_data
            self.save_welcome_data()
            await message.reply_text("✅ Welcome message saved successfully!")
        elif message_type == "broadcast":
            # NEW: Save broadcast message and send to all users
            await self.broadcast_message_to_all_users(message, message_data)
            
        # Clear admin state
        user_id = update.effective_user.id
        if user_id in self.admin_states:
            del self.admin_states[user_id]
            
    async def broadcast_message_to_all_users(self, message, message_data):
        """NEW: Send message to all users"""
        if not self.users:
            await message.reply_text("❌ No users found to broadcast to.")
            return
            
        # Save broadcast message data
        with open("broadcast_data.json", 'w', encoding='utf-8') as f:
            json.dump(message_data, f, indent=2, ensure_ascii=False)
            
        # Send to all users
        success_count = 0
        failed_count = 0
        
        await message.reply_text(f"📡 Broadcasting message to {len(self.users)} users...")
        
        for user_id, user_info in self.users.items():
            try:
                if message_data["type"] == "text":
                    await message.bot.send_message(
                        chat_id=int(user_id),
                        text=message_data["content"]
                    )
                elif message_data["type"] == "photo":
                    await message.bot.send_photo(
                        chat_id=int(user_id),
                        photo=message_data["file_id"],
                        caption=message_data.get("caption")
                    )
                elif message_data["type"] == "video":
                    await message.bot.send_video(
                        chat_id=int(user_id),
                        video=message_data["file_id"],
                        caption=message_data.get("caption")
                    )
                elif message_data["type"] == "voice":
                    await message.bot.send_voice(
                        chat_id=int(user_id),
                        voice=message_data["file_id"],
                        caption=message_data.get("caption")
                    )
                elif message_data["type"] == "audio":
                    await message.bot.send_audio(
                        chat_id=int(user_id),
                        audio=message_data["file_id"],
                        caption=message_data.get("caption")
                    )
                elif message_data["type"] == "document":
                    await message.bot.send_document(
                        chat_id=int(user_id),
                        document=message_data["file_id"],
                        caption=message_data.get("caption")
                    )
                elif message_data["type"] == "video_note":
                    await message.bot.send_video_note(
                        chat_id=int(user_id),
                        video_note=message_data["file_id"]
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
        
    def log_broadcast(self, success_count: int, failed_count: int, total_users: int):
        """Log broadcast activity"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] BROADCAST - Success: {success_count}, Failed: {failed_count}, Total: {total_users}\n"
        
        with open(self.LOGS_FILE, 'a') as f:
            f.write(log_entry)
            
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
        
        # Callback query handler for inline buttons
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Message handler for admin responses (support all message types)
        self.application.add_handler(MessageHandler(
            (filters.TEXT | filters.VOICE | filters.PHOTO | filters.VIDEO | 
             filters.Document.ALL | filters.AUDIO | filters.VIDEO_NOTE) & ~filters.COMMAND, 
            self.handle_message
        ))
        
        # Join request handler
        self.application.add_handler(ChatJoinRequestHandler(self.handle_join_request))
        
        # New chat member handler (for when bot is added to channels)
        self.application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.handle_new_chat_members))
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Store user information (NEW)
        if str(user.id) not in self.users:
            self.users[str(user.id)] = {
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "joined_date": datetime.now().isoformat()
            }
            self.save_users()
        
        await update.message.reply_text(
            "🤖 Welcome to the Auto-Join Bot!\n\n"
            "This bot automatically approves join requests and sends welcome messages.\n\n"
            "Use /admin to access the admin panel (admin only)."
        )
        
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command - show admin panel"""
        user_id = update.effective_user.id
        
        if user_id not in self.admins:
            await update.message.reply_text("❌ Access denied. You are not authorized as an admin.")
            return
            
        await self.show_admin_panel(update, context)
        
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
            f"**To add this to your bot:**\n"
            f"1. Copy the ID: `{chat.id}`\n"
            f"2. Send `/admin` to your bot\n"
            f"3. Click '📢 Manage Channels'\n"
            f"4. Click '➕ Add Channel'\n"
            f"5. Paste the ID: `{chat.id}`",
            parse_mode='Markdown'
        )
        
    async def show_admin_panel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show the admin panel with inline buttons"""
        keyboard = [
            [
                InlineKeyboardButton("📩 Set Welcome Message", callback_data="set_welcome"),
                InlineKeyboardButton("📬 Preview Welcome Message", callback_data="preview_welcome")
            ],
            [
                InlineKeyboardButton("🗑️ Delete Welcome Message", callback_data="delete_welcome"),
                InlineKeyboardButton("📡 Send Message to All Users", callback_data="send_broadcast")
            ],
            [
                InlineKeyboardButton("👥 View User Stats", callback_data="view_users"),
                InlineKeyboardButton("📢 Manage Channels", callback_data="manage_channels")
            ],
            [
                InlineKeyboardButton("📑 View Logs", callback_data="view_logs"),
                InlineKeyboardButton("🛑 Stop Bot", callback_data="stop_bot")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🔧 **Admin Panel**\n\n"
            "Welcome to the admin panel. Use the buttons below to manage the bot:",
            reply_markup=reply_markup
        )
        
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline buttons"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        if user_id not in self.admins:
            await query.edit_message_text("❌ Access denied. You are not authorized as an admin.")
            return
            
        if data == "set_welcome":
            self.admin_states[user_id] = "waiting_welcome"
            await query.edit_message_text(
                "📩 **Set Welcome Message**\n\n"
                "Send the new welcome message. Supported types:\n"
                "• Text\n"
                "• Photo\n"
                "• Video\n"
                "• Voice\n"
                "• Audio\n"
                "• Document\n"
                "• Video Note\n\n"
                "This message will be sent to new members when they join."
            )
            
        elif data == "preview_welcome":
            if self.welcome_message_data:
                if self.welcome_message_data["type"] == "text":
                    await query.edit_message_text(
                        f"📬 **Current Welcome Message**\n\n"
                        f"**Type:** Text\n"
                        f"**Content:**\n{self.welcome_message_data['content']}"
                    )
                else:
                    await query.edit_message_text(
                        f"📬 **Current Welcome Message**\n\n"
                        f"**Type:** {self.welcome_message_data['type'].upper()}\n"
                        f"**Caption:** {self.welcome_message_data.get('caption', 'None')}"
                    )
            else:
                await query.edit_message_text(
                    "📬 **Current Welcome Message**\n\n"
                    "No welcome message set. Use '📩 Set Welcome Message' to set one."
                )
                
        elif data == "delete_welcome":
            self.welcome_message_data = None
            self.save_welcome_data()
            await query.edit_message_text("✅ Welcome message deleted successfully!")
            
        elif data == "send_broadcast":
            self.admin_states[user_id] = "waiting_broadcast"
            await query.edit_message_text(
                "📡 **Send Message to All Users**\n\n"
                "Send the message you want to broadcast to all users. Supported types:\n"
                "• Text\n"
                "• Photo\n"
                "• Video\n"
                "• Voice\n"
                "• Audio\n"
                "• Document\n"
                "• Video Note\n\n"
                f"**Total users:** {len(self.users)}\n"
                "⚠️ **Warning:** This will send the message to ALL users who have interacted with the bot!"
            )
            
        elif data == "view_users":
            await self.show_user_stats(query)
            
        elif data == "manage_channels":
            await self.show_channel_management(query)
            
        elif data == "view_logs":
            await self.show_logs(query)
            
        elif data == "stop_bot":
            await self.stop_bot(query)
            
        elif data == "back_to_admin":
            await self.show_admin_panel_from_query(query, context)
            
        elif data == "add_channel":
            self.admin_states[user_id] = "waiting_channel"
            await query.edit_message_text(
                "📢 **Add Channel**\n\n"
                "**Method 1: Forward Message**\n"
                "1. Add bot to your channel as admin\n"
                "2. Forward any message from channel to this chat\n\n"
                "**Method 2: Send Channel Username**\n"
                "Send: @channelname (public channels only)\n\n"
                "**Method 3: Send Channel ID**\n"
                "Send: -1001234567890\n\n"
                "**Note:** Make sure the bot is added to the channel as admin!"
            )
            
        elif data == "list_channels":
            await self.list_channels(query)
            
        elif data == "remove_channel":
            await self.show_channel_removal(query)
            
        elif data.startswith("remove_"):
            channel_id = data.split("_")[1]
            if channel_id in self.channels:
                channel_name = self.channels[channel_id]["name"]
                del self.channels[channel_id]
                self.save_channels()
                await query.edit_message_text(f"✅ Channel '{channel_name}' removed successfully!")
            else:
                await query.edit_message_text("❌ Channel not found!")
                
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
        
    async def show_channel_management(self, query):
        """Show channel management options"""
        keyboard = [
            [
                InlineKeyboardButton("➕ Add Channel", callback_data="add_channel"),
                InlineKeyboardButton("📋 List Channels", callback_data="list_channels")
            ],
            [
                InlineKeyboardButton("🗑️ Remove Channel", callback_data="remove_channel"),
                InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📢 **Channel Management**\n\n"
            "Manage the channels where the bot will work:",
            reply_markup=reply_markup
        )
        
    async def list_channels(self, query):
        """List all configured channels"""
        if not self.channels:
            await query.edit_message_text(
                "📋 **No Channels Configured**\n\n"
                "No channels have been added yet. Use '➕ Add Channel' to add one.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Channel Management", callback_data="manage_channels")
                ]])
            )
            return
            
        channel_list = "\n".join([
            f"• **{info['name']}** (ID: `{channel_id}`)"
            for channel_id, info in self.channels.items()
        ])
        
        await query.edit_message_text(
            f"📋 **Configured Channels**\n\n{channel_list}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Channel Management", callback_data="manage_channels")
            ]]),
            parse_mode='Markdown'
        )
        
    async def show_channel_removal(self, query):
        """Show channel removal options"""
        if not self.channels:
            await query.edit_message_text(
                "🗑️ **No Channels to Remove**\n\n"
                "No channels have been configured yet.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Channel Management", callback_data="manage_channels")
                ]])
            )
            return
            
        keyboard = []
        for channel_id, info in self.channels.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"🗑️ {info['name']}", 
                    callback_data=f"remove_{channel_id}"
                )
            ])
            
        keyboard.append([InlineKeyboardButton("🔙 Back to Channel Management", callback_data="manage_channels")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🗑️ **Remove Channel**\n\n"
            "Select a channel to remove:",
            reply_markup=reply_markup
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
        """Handle incoming messages"""
        user_id = update.effective_user.id
        
        # Check if user is waiting for a response
        if user_id in self.admin_states:
            state = self.admin_states[user_id]
            
            if state == "waiting_welcome":
                await self.save_message_by_type(update, context, "welcome")
            elif state == "waiting_broadcast":
                await self.save_message_by_type(update, context, "broadcast")
            elif state == "waiting_channel":
                await self.handle_channel_input(update, context)
                
    async def handle_channel_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle channel input from admin"""
        message = update.message
        text = message.text.strip()
        
        # Check if it's a forwarded message
        if message.forward_from_chat:
            chat = message.forward_from_chat
            if chat.type in ['channel', 'supergroup', 'group']:
                self.channels[str(chat.id)] = {
                    "name": chat.title,
                    "type": chat.type,
                    "username": chat.username
                }
                self.save_channels()
                await message.reply_text(f"✅ Channel '{chat.title}' added successfully!")
                
                # Clear admin state
                user_id = update.effective_user.id
                if user_id in self.admin_states:
                    del self.admin_states[user_id]
                return
                
        # Check if it's a username
        if text.startswith('@'):
            username = text[1:]
            try:
                chat = await context.bot.get_chat(f"@{username}")
                if chat.type in ['channel', 'supergroup', 'group']:
                    self.channels[str(chat.id)] = {
                        "name": chat.title,
                        "type": chat.type,
                        "username": chat.username
                    }
                    self.save_channels()
                    await message.reply_text(f"✅ Channel '{chat.title}' added successfully!")
                    
                    # Clear admin state
                    user_id = update.effective_user.id
                    if user_id in self.admin_states:
                        del self.admin_states[user_id]
                    return
            except Exception as e:
                await message.reply_text(f"❌ Error adding channel: {str(e)}")
                return
                
        # Check if it's a channel ID
        try:
            channel_id = int(text)
            if channel_id < 0:  # Channel IDs are negative
                try:
                    chat = await context.bot.get_chat(channel_id)
                    if chat.type in ['channel', 'supergroup', 'group']:
                        self.channels[str(channel_id)] = {
                            "name": chat.title,
                            "type": chat.type,
                            "username": chat.username
                        }
                        self.save_channels()
                        await message.reply_text(f"✅ Channel '{chat.title}' added successfully!")
                        
                        # Clear admin state
                        user_id = update.effective_user.id
                        if user_id in self.admin_states:
                            del self.admin_states[user_id]
                        return
                except Exception as e:
                    await message.reply_text(f"❌ Error adding channel: {str(e)}")
                    return
        except ValueError:
            pass
            
        await message.reply_text(
            "❌ **Invalid Input**\n\n"
            "Please provide:\n"
            "• A forwarded message from the channel\n"
            "• Channel username (e.g., @channelname)\n"
            "• Channel ID (e.g., -1001234567890)"
        )
        
    async def handle_join_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle join requests"""
        join_request = update.chat_join_request
        
        try:
            # Approve the join request
            await context.bot.approve_chat_join_request(
                chat_id=join_request.chat.id,
                user_id=join_request.from_user.id
            )
            
            # Send welcome message if configured
            if self.welcome_message_data:
                try:
                    await self.send_welcome_message(context.bot, join_request.from_user.id)
                    self.log_join(join_request.from_user.username, join_request.from_user.id, True)
                except Exception as e:
                    self.log_join(join_request.from_user.username, join_request.from_user.id, False, str(e))
            else:
                self.log_join(join_request.from_user.username, join_request.from_user.id, True)
                
        except Exception as e:
            logger.error(f"Error handling join request: {e}")
            self.log_join(join_request.from_user.username, join_request.from_user.id, False, str(e))
            
    async def handle_new_chat_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle new chat members (when bot is added to channels)"""
        for new_member in update.message.new_chat_members:
            if new_member.id == context.bot.id:
                # Bot was added to a chat
                chat = update.effective_chat
                if chat.type in ['channel', 'supergroup', 'group']:
                    self.channels[str(chat.id)] = {
                        "name": chat.title,
                        "type": chat.type,
                        "username": chat.username
                    }
                    self.save_channels()
                    
                    await update.message.reply_text(
                        f"✅ Bot added to '{chat.title}' successfully!\n"
                        f"This channel is now configured for auto-join requests."
                    )
                    
    async def send_welcome_message(self, bot, user_id: int):
        """Send welcome message to user"""
        if not self.welcome_message_data:
            return
            
        try:
            if self.welcome_message_data["type"] == "text":
                await bot.send_message(
                    chat_id=user_id,
                    text=self.welcome_message_data["content"]
                )
            elif self.welcome_message_data["type"] == "photo":
                await bot.send_photo(
                    chat_id=user_id,
                    photo=self.welcome_message_data["file_id"],
                    caption=self.welcome_message_data.get("caption")
                )
            elif self.welcome_message_data["type"] == "video":
                await bot.send_video(
                    chat_id=user_id,
                    video=self.welcome_message_data["file_id"],
                    caption=self.welcome_message_data.get("caption")
                )
            elif self.welcome_message_data["type"] == "voice":
                await bot.send_voice(
                    chat_id=user_id,
                    voice=self.welcome_message_data["file_id"],
                    caption=self.welcome_message_data.get("caption")
                )
            elif self.welcome_message_data["type"] == "audio":
                await bot.send_audio(
                    chat_id=user_id,
                    audio=self.welcome_message_data["file_id"],
                    caption=self.welcome_message_data.get("caption")
                )
            elif self.welcome_message_data["type"] == "document":
                await bot.send_document(
                    chat_id=user_id,
                    document=self.welcome_message_data["file_id"],
                    caption=self.welcome_message_data.get("caption")
                )
            elif self.welcome_message_data["type"] == "video_note":
                await bot.send_video_note(
                    chat_id=user_id,
                    video_note=self.welcome_message_data["file_id"]
                )
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")
            raise e
            
    def run(self):
        """Run the bot"""
        print("🚀 Starting bot...")
        self.application.run_polling()

def main():
    """Main function"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        print("Please set your bot token:")
        print("export TELEGRAM_BOT_TOKEN='your_bot_token_here'")
        return
        
    bot = TelegramBot(token)
    bot.run()

if __name__ == "__main__":
    main()
