#!/usr/bin/env python3
"""
Telegram Bot with Auto-Join Request Approval, Welcome Messages, and Admin Panel
Features:
- Auto-accept join requests
- Send welcome DM to new members
- Admin panel with inline buttons
- Scheduled messaging
- File-based configuration (no database)
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, List, Optional

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, continue without it
    pass

from telegram import (
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    Update,
    ChatJoinRequest
)
from telegram.ext import (
    Application, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler,
    ChatJoinRequestHandler,
    ContextTypes,
    filters
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# File paths for configuration
WELCOME_FILE = "welcome.txt"
SCHEDULE_FILE = "schedule.txt"
INTERVAL_FILE = "interval.txt"
ADMINS_FILE = "admins.json"
LOGS_FILE = "logs.txt"
CHANNELS_FILE = "channels.json"

# Default values
DEFAULT_WELCOME = "Welcome to our group! 🎉\n\nWe're glad to have you here. Please read the rules and enjoy your stay!"
DEFAULT_SCHEDULE = "📢 Reminder: Don't forget to check the latest updates in our group!"
DEFAULT_INTERVAL = 24  # hours

class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(token).build()
        self.scheduler = AsyncIOScheduler()
        self.admin_states = {}  # Track admin conversation states
        self.setup_handlers()
        self.load_config()
        
    def load_config(self):
        """Load configuration from files"""
        # Load admins
        if os.path.exists(ADMINS_FILE):
            with open(ADMINS_FILE, 'r') as f:
                self.admins = json.load(f)
        else:
            self.admins = []
            self.save_admins()
            
        # Load channels
        if os.path.exists(CHANNELS_FILE):
            with open(CHANNELS_FILE, 'r') as f:
                self.channels = json.load(f)
        else:
            self.channels = {}
            self.save_channels()
            
        # Load welcome message data
        self.welcome_message_data = self.load_message_data("welcome")
        if not self.welcome_message_data:
            self.welcome_message_data = {
                "type": "text",
                "content": DEFAULT_WELCOME
            }
            self.save_welcome_data()
            
        # Load scheduled message data
        self.scheduled_message_data = self.load_message_data("schedule")
        if not self.scheduled_message_data:
            self.scheduled_message_data = {
                "type": "text",
                "content": DEFAULT_SCHEDULE
            }
            self.save_schedule_data()
            
        # Load channel-specific messages
        try:
            with open("channel_messages.json", 'r') as f:
                self.channel_messages = json.load(f)
        except FileNotFoundError:
            self.channel_messages = {}
            
        # Load interval
        if os.path.exists(INTERVAL_FILE):
            with open(INTERVAL_FILE, 'r') as f:
                self.interval = int(f.read().strip())
        else:
            self.interval = DEFAULT_INTERVAL
            self.save_interval()
            
        # Create logs file if not exists
        if not os.path.exists(LOGS_FILE):
            with open(LOGS_FILE, 'w', encoding='utf-8') as f:
                f.write("")
                
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
        with open("welcome_data.json", 'w', encoding='utf-8') as f:
            json.dump(self.welcome_message_data, f, indent=2, ensure_ascii=False)
            
    def save_schedule_data(self):
        """Save scheduled message data to JSON file"""
        with open("schedule_data.json", 'w', encoding='utf-8') as f:
            json.dump(self.scheduled_message_data, f, indent=2, ensure_ascii=False)
            
    def save_channels(self):
        """Save channels to file"""
        with open(CHANNELS_FILE, 'w') as f:
            json.dump(self.channels, f, indent=2)
                
    def save_admins(self):
        """Save admin list to file"""
        with open(ADMINS_FILE, 'w') as f:
            json.dump(self.admins, f)
            
    def save_welcome(self):
        """Save welcome message to file"""
        with open(WELCOME_FILE, 'w', encoding='utf-8') as f:
            f.write(self.welcome_message)
            
    def save_schedule(self):
        """Save scheduled message to file"""
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
            f.write(self.scheduled_message)
            
    def save_interval(self):
        """Save interval to file"""
        with open(INTERVAL_FILE, 'w') as f:
            f.write(str(self.interval))
            
    def save_channel_messages(self):
        """Save channel messages to file"""
        with open("channel_messages.json", 'w') as f:
            json.dump(self.channel_messages, f, indent=2)
            
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
            # Get the largest photo size
            largest_photo = max(message.photo, key=lambda p: p.file_size)
            message_data["file_id"] = largest_photo.file_id
            message_data["caption"] = message.caption
        elif message.video:
            message_data["type"] = "video"
            message_data["file_id"] = message.video.file_id
            message_data["caption"] = message.caption
        elif message.document:
            message_data["type"] = "document"
            message_data["file_id"] = message.document.file_id
            message_data["caption"] = message.caption
        elif message.audio:
            message_data["type"] = "audio"
            message_data["file_id"] = message.audio.file_id
            message_data["caption"] = message.caption
        elif message.video_note:
            message_data["type"] = "video_note"
            message_data["file_id"] = message.video_note.file_id
        else:
            # Fallback to text if no recognized type
            message_data["type"] = "text"
            message_data["content"] = "Unsupported message type"
        
        # Save to appropriate file
        if message_type == "welcome":
            self.welcome_message_data = message_data
            self.save_welcome_data()
        elif message_type == "schedule":
            self.scheduled_message_data = message_data
            self.save_schedule_data()
            
    async def save_channel_message_by_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE, channel_id: str, message_type: str):
        """Save channel-specific message based on its type"""
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
            # Get the largest photo size
            largest_photo = max(message.photo, key=lambda p: p.file_size)
            message_data["file_id"] = largest_photo.file_id
            message_data["caption"] = message.caption
        elif message.video:
            message_data["type"] = "video"
            message_data["file_id"] = message.video.file_id
            message_data["caption"] = message.caption
        elif message.document:
            message_data["type"] = "document"
            message_data["file_id"] = message.document.file_id
            message_data["caption"] = message.caption
        elif message.audio:
            message_data["type"] = "audio"
            message_data["file_id"] = message.audio.file_id
            message_data["caption"] = message.caption
        elif message.video_note:
            message_data["type"] = "video_note"
            message_data["file_id"] = message.video_note.file_id
        else:
            # Fallback to text if no recognized type
            message_data["type"] = "text"
            message_data["content"] = "Unsupported message type"
        
        # Save to channel-specific messages
        if channel_id not in self.channel_messages:
            self.channel_messages[channel_id] = {}
            
        self.channel_messages[channel_id][message_type] = message_data
        self.save_channel_messages()
            
    def log_join(self, username: str, user_id: int, dm_sent: bool, error: str = None):
        """Log join request details"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "✅ DM sent" if dm_sent else f"❌ DM failed: {error}" if error else "❌ DM failed"
        
        log_entry = f"[{timestamp}] @{username} (ID: {user_id}) - {status}\n"
        
        with open(LOGS_FILE, 'a', encoding='utf-8') as f:
            f.write(log_entry)
            
    def setup_handlers(self):
        """Setup all bot handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("id", self.show_chat_id))
        
        # Join request handler
        self.application.add_handler(ChatJoinRequestHandler(self.handle_join_request))
        
        # New chat member handler (for when bot is added to channels)
        self.application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.handle_new_chat_members))
        
        # Callback query handler for inline buttons
        self.application.add_handler(CallbackQueryHandler(self.handle_callback))
        
        # Message handler for admin responses (support all message types)
        self.application.add_handler(MessageHandler(
            (filters.TEXT | filters.VOICE | filters.PHOTO | filters.VIDEO | 
             filters.Document.ALL | filters.AUDIO | filters.VIDEO_NOTE) & ~filters.COMMAND, 
            self.handle_message
        ))
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
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
                InlineKeyboardButton("🕒 Set Scheduled Message", callback_data="set_schedule")
            ],
            [
                InlineKeyboardButton("📢 Manage Channels", callback_data="manage_channels"),
                InlineKeyboardButton("⏱ Set Interval", callback_data="set_interval")
            ],
            [
                InlineKeyboardButton("🔁 Toggle Scheduler", callback_data="toggle_scheduler"),
                InlineKeyboardButton("📑 View Logs", callback_data="view_logs")
            ],
            [
                InlineKeyboardButton("🛑 Stop Bot", callback_data="stop_bot")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "🔧 **Admin Panel**\n\nSelect an option:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                "🔧 **Admin Panel**\n\nSelect an option:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        if user_id not in self.admins:
            await query.edit_message_text("❌ Access denied. You are not authorized as an admin.")
            return
            
        data = query.data
        
        if data == "set_welcome":
            self.admin_states[user_id] = "waiting_welcome"
            await query.edit_message_text(
                "📩 **Set Welcome Message**\n\n"
                "Please select a channel to set the welcome message for.",
                parse_mode='Markdown'
            )
            await self.show_channel_selection_for_welcome(query)
            
        elif data == "preview_welcome":
            if self.welcome_message_data and self.welcome_message_data.get("type") == "text":
                message_text = self.welcome_message_data.get("content", "No welcome message set")
                await query.edit_message_text(
                    f"📬 **Current Welcome Message:**\n\n{message_text}",
                    parse_mode='Markdown'
                )
            else:
                message_type = self.welcome_message_data.get("type", "text") if self.welcome_message_data else "text"
                await query.edit_message_text(
                    f"📬 **Current Welcome Message:**\n\nType: {message_type.upper()}\n\nUse the admin panel to set a new message.",
                    parse_mode='Markdown'
                )
            
        elif data == "set_schedule":
            self.admin_states[user_id] = "waiting_schedule"
            await query.edit_message_text(
                "🕒 **Set Scheduled Message**\n\n"
                "Please select a channel to set the scheduled message for.",
                parse_mode='Markdown'
            )
            await self.show_channel_selection_for_schedule(query)
            
        elif data == "preview_schedule":
            if self.scheduled_message_data and self.scheduled_message_data.get("type") == "text":
                message_text = self.scheduled_message_data.get("content", "No scheduled message set")
                await query.edit_message_text(
                    f"📤 **Current Scheduled Message:**\n\n{message_text}",
                    parse_mode='Markdown'
                )
            else:
                message_type = self.scheduled_message_data.get("type", "text") if self.scheduled_message_data else "text"
                await query.edit_message_text(
                    f"📤 **Current Scheduled Message:**\n\nType: {message_type.upper()}\n\nUse the admin panel to set a new message.",
                    parse_mode='Markdown'
                )
            
        elif data == "delete_welcome":
            self.welcome_message_data = None
            self.save_welcome_data()
            await query.edit_message_text(
                "🗑️ **Welcome Message Deleted**\n\nWelcome message has been cleared.",
                parse_mode='Markdown'
            )
            
        elif data == "delete_schedule":
            self.scheduled_message_data = None
            self.save_schedule_data()
            await query.edit_message_text(
                "🗑️ **Scheduled Message Deleted**\n\nScheduled message has been cleared.",
                parse_mode='Markdown'
            )
            
        elif data == "set_interval":
            await self.show_interval_options(query)
            
        elif data == "toggle_scheduler":
            await self.toggle_scheduler(query)
            
        elif data == "view_logs":
            await self.show_logs(query)
            
        elif data == "stop_bot":
            await self.stop_bot(query)
            
        elif data.startswith("interval_"):
            interval = int(data.split("_")[1])
            self.interval = interval
            self.save_interval()
            await query.edit_message_text(
                f"⏱ **Interval Updated**\n\nScheduled messages will be sent every {interval} hours.",
                parse_mode='Markdown'
            )
            
        elif data == "manage_channels":
            await self.show_channel_management(query)
            
        elif data == "channel_messages":
            await self.show_channel_messages_menu(query)
            
        elif data.startswith("channel_welcome_"):
            channel_id = data.split("_")[2]
            if channel_id in self.channels:
                self.admin_states[user_id] = f"waiting_channel_welcome_{channel_id}"
                channel_name = self.channels[channel_id]["name"]
                await query.edit_message_text(
                    f"📩 **Set Welcome Message for {channel_name}**\n\n"
                    "Please send the welcome message for this specific channel.\n\n"
                    "**Supported types:**\n"
                    "• Text messages\n"
                    "• Photos (with caption)\n"
                    "• Videos (with caption)\n"
                    "• Voice messages\n"
                    "• Audio files\n"
                    "• Documents\n"
                    "• Video notes\n"
                    "• Stickers",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(
                    "❌ **Channel Not Found**\n\nThis channel is not configured in the bot.",
                    parse_mode='Markdown'
                )
                
        elif data.startswith("channel_schedule_"):
            channel_id = data.split("_")[2]
            if channel_id in self.channels:
                self.admin_states[user_id] = f"waiting_channel_schedule_{channel_id}"
                channel_name = self.channels[channel_id]["name"]
                await query.edit_message_text(
                    f"🕒 **Set Scheduled Message for {channel_name}**\n\n"
                    "Please send the scheduled message for this specific channel.\n\n"
                    "**Supported types:**\n"
                    "• Text messages\n"
                    "• Photos (with caption)\n"
                    "• Videos (with caption)\n"
                    "• Voice messages\n"
                    "• Audio files\n"
                    "• Documents\n"
                    "• Video notes\n"
                    "• Stickers",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(
                    "❌ **Channel Not Found**\n\nThis channel is not configured in the bot.",
                    parse_mode='Markdown'
                )
                
        elif data.startswith("channel_schedule_"):
            channel_id = data.split("_")[2]
            if channel_id in self.channels:
                self.admin_states[user_id] = f"waiting_channel_schedule_{channel_id}"
                channel_name = self.channels[channel_id]["name"]
                await query.edit_message_text(
                    f"🕒 **Set Scheduled Message for {channel_name}**\n\n"
                    "Please send the scheduled message for this specific channel.\n\n"
                    "**Supported types:**\n"
                    "• Text messages\n"
                    "• Photos (with caption)\n"
                    "• Videos (with caption)\n"
                    "• Voice messages\n"
                    "• Audio files\n"
                    "• Documents\n"
                    "• Video notes",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text("❌ Channel not found!")
            
        elif data == "list_channels":
            await self.list_channels(query)
            
        elif data == "add_channel":
            self.admin_states[user_id] = "waiting_channel"
            await query.edit_message_text(
                "📢 **Add Channel**\n\n"
                "**Method 1: Forward Message**\n"
                "1. Add bot to your channel as admin\n"
                "2. Forward any message from channel to this chat\n\n"
                "**Method 2: Send Channel Username**\n"
                "Send: `@channelname` (public channels only)\n\n"
                "**Method 3: Send Channel ID**\n"
                "Send: `-1001234567890`\n\n"
                "**Note:** For private channels, use Method 1 (forward message)",
                parse_mode='Markdown'
            )
            
        elif data == "remove_channel":
            await self.show_channel_removal(query)
            
        elif data.startswith("remove_channel_"):
            channel_id = data.split("_")[2]
            if channel_id in self.channels:
                channel_name = self.channels[channel_id]["name"]
                del self.channels[channel_id]
                self.save_channels()
                await query.edit_message_text(
                    f"🗑️ **Channel Removed**\n\nChannel '{channel_name}' has been removed.",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text(
                    "❌ **Error**\n\nChannel not found.",
                    parse_mode='Markdown'
                )
            
        elif data == "back_to_admin":
            await self.show_admin_panel(update, context)
            
    async def show_channel_selection_for_welcome(self, query):
        """Show a list of channels for setting the welcome message."""
        keyboard = []
        for channel_id, channel_info in self.channels.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"📩 {channel_info['name']}", 
                    callback_data=f"channel_welcome_{channel_id}"
                )
            ])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_admin")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📩 **Select a Channel for Welcome Message**\n\nChoose a channel from the list:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    async def show_channel_selection_for_schedule(self, query):
        """Show a list of channels for setting the scheduled message."""
        keyboard = []
        for channel_id, channel_info in self.channels.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"🕒 {channel_info['name']}", 
                    callback_data=f"channel_schedule_{channel_id}"
                )
            ])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_admin")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🕒 **Select a Channel for Scheduled Message**\n\nChoose a channel from the list:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    async def show_interval_options(self, query):
        """Show interval selection buttons"""
        keyboard = [
            [
                InlineKeyboardButton("Every 1h", callback_data="interval_1"),
                InlineKeyboardButton("Every 3h", callback_data="interval_3"),
                InlineKeyboardButton("Every 5h", callback_data="interval_5")
            ],
            [
                InlineKeyboardButton("Every 12h", callback_data="interval_12"),
                InlineKeyboardButton("Every 24h", callback_data="interval_24")
            ],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_admin")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "⏱ **Set Interval**\n\nChoose how often to send scheduled messages:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    async def toggle_scheduler(self, query):
        """Toggle the scheduler on/off"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            status = "🛑 **Scheduler Stopped**"
            button_text = "▶️ Start Scheduler"
        else:
            self.scheduler.start()
            self.scheduler.add_job(
                self.send_scheduled_message,
                IntervalTrigger(hours=self.interval),
                id='scheduled_message',
                replace_existing=True
            )
            status = "▶️ **Scheduler Started**"
            button_text = "🛑 Stop Scheduler"
            
        keyboard = [
            [InlineKeyboardButton(button_text, callback_data="toggle_scheduler")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_admin")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"{status}\n\nScheduled messages will be sent every {self.interval} hours.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    async def show_logs(self, query):
        """Show recent join logs"""
        try:
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                logs = f.read().strip()
                
            if not logs:
                logs = "No logs available yet."
            else:
                # Show last 10 entries
                log_lines = logs.split('\n')[-10:]
                logs = '\n'.join(log_lines)
                
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_admin")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                f"📑 **Recent Join Logs**\n\n```\n{logs}\n```",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            await query.edit_message_text(
                f"❌ Error reading logs: {str(e)}",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="back_to_admin")]])
            )
            
    async def stop_bot(self, query):
        """Stop the bot gracefully"""
        keyboard = [
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_admin")],
            [InlineKeyboardButton("🛑 Confirm Stop", callback_data="confirm_stop")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🛑 **Stop Bot**\n\nAre you sure you want to stop the bot?",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all message types (for admin responses)"""
        # Check if effective_user exists
        if not update.effective_user:
            return
            
        user_id = update.effective_user.id
        
        if user_id not in self.admins:
            return
            
        if user_id not in self.admin_states:
            return
            
        state = self.admin_states[user_id]
        
        if state == "waiting_welcome":
            # Save the message based on its type
            await self.save_message_by_type(update, context, "welcome")
            del self.admin_states[user_id]
            
            keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "✅ **Welcome Message Updated**\n\nNew welcome message has been saved.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        elif state == "waiting_schedule":
            # Save the message based on its type
            await self.save_message_by_type(update, context, "schedule")
            del self.admin_states[user_id]
            
            keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "✅ **Scheduled Message Updated**\n\nNew scheduled message has been saved.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            
        elif state == "waiting_channel":
            # Handle channel addition
            await self.handle_channel_addition(update, context)
            del self.admin_states[user_id]
            
        elif state.startswith("waiting_channel_welcome_"):
            # Handle channel-specific welcome message
            channel_id = state.split("_")[3]
            if channel_id in self.channels:
                await self.save_channel_message_by_type(update, context, channel_id, "welcome")
                channel_name = self.channels[channel_id]["name"]
                
                keyboard = [[InlineKeyboardButton("🔙 Back to Channel Messages", callback_data="channel_messages")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    f"✅ **Welcome Message Updated for {channel_name}**\n\nChannel-specific welcome message has been saved.",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            del self.admin_states[user_id]
            
        elif state.startswith("waiting_channel_schedule_"):
            # Handle channel-specific scheduled message
            channel_id = state.split("_")[3]
            if channel_id in self.channels:
                await self.save_channel_message_by_type(update, context, channel_id, "schedule")
                channel_name = self.channels[channel_id]["name"]
                
                keyboard = [[InlineKeyboardButton("🔙 Back to Channel Messages", callback_data="channel_messages")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(
                    f"✅ **Scheduled Message Updated for {channel_name}**\n\nChannel-specific scheduled message has been saved.",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
            del self.admin_states[user_id]
            
    async def handle_channel_addition(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle channel addition from admin"""
        message = update.message
        
        try:
            # Check if it's a forwarded message from a channel
            if hasattr(message, 'forward_from_chat') and message.forward_from_chat:
                chat = message.forward_from_chat
                if chat.type in ['channel', 'supergroup']:
                    channel_id = str(chat.id)
                    channel_name = chat.title
                    channel_type = chat.type
                    
                    # Add channel to configuration
                    self.channels[channel_id] = {
                        "name": channel_name,
                        "type": channel_type,
                        "username": chat.username
                    }
                    self.save_channels()
                    
                    keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await message.reply_text(
                        f"✅ **Channel Added**\n\n"
                        f"**Name:** {channel_name}\n"
                        f"**ID:** `{channel_id}`\n"
                        f"**Type:** {channel_type}\n\n"
                        f"Channel has been added successfully!",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    return
                else:
                    await message.reply_text("❌ **Error**\n\nThis is not a channel or supergroup.")
                    return
                    
            # Check if it's a channel username or ID
            elif message.text:
                text = message.text.strip()
                
                if text.startswith('@'):
                    # Username format
                    username = text[1:]  # Remove @
                    try:
                        chat = await context.bot.get_chat(f"@{username}")
                        if chat.type in ['channel', 'supergroup']:
                            channel_id = str(chat.id)
                            channel_name = chat.title
                            channel_type = chat.type
                            
                            self.channels[channel_id] = {
                                "name": channel_name,
                                "type": channel_type,
                                "username": chat.username
                            }
                            self.save_channels()
                            
                            keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin")]]
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            
                            await message.reply_text(
                                f"✅ **Channel Added**\n\n"
                                f"**Name:** {channel_name}\n"
                                f"**ID:** `{channel_id}`\n"
                                f"**Type:** {channel_type}\n\n"
                                f"Channel has been added successfully!",
                                reply_markup=reply_markup,
                                parse_mode='Markdown'
                            )
                        else:
                            await message.reply_text("❌ **Error**\n\nThis is not a channel or supergroup.")
                    except Exception as e:
                        await message.reply_text(f"❌ **Error**\n\nCould not find channel: {e}")
                        
                elif text.startswith('-100'):
                    # Channel ID format
                    try:
                        chat = await context.bot.get_chat(text)
                        if chat.type in ['channel', 'supergroup']:
                            channel_id = str(chat.id)
                            channel_name = chat.title
                            channel_type = chat.type
                            
                            self.channels[channel_id] = {
                                "name": channel_name,
                                "type": channel_type,
                                "username": chat.username
                            }
                            self.save_channels()
                            
                            keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin")]]
                            reply_markup = InlineKeyboardMarkup(keyboard)
                            
                            await message.reply_text(
                                f"✅ **Channel Added**\n\n"
                                f"**Name:** {channel_name}\n"
                                f"**ID:** `{channel_id}`\n"
                                f"**Type:** {channel_type}\n\n"
                                f"Channel has been added successfully!",
                                reply_markup=reply_markup,
                                parse_mode='Markdown'
                            )
                        else:
                            await message.reply_text("❌ **Error**\n\nThis is not a channel or supergroup.")
                    except Exception as e:
                        await message.reply_text(f"❌ **Error**\n\nCould not find channel: {e}")
                else:
                    await message.reply_text(
                        "❌ **Invalid Format**\n\n"
                        "Please send:\n"
                        "• A forwarded message from the channel\n"
                        "• Channel username (e.g., @channelname)\n"
                        "• Channel ID (e.g., -1001234567890)"
                    )
            else:
                # Try to get channel info from the message itself
                if hasattr(message, 'chat') and message.chat.type in ['channel', 'supergroup']:
                    # This is a message from a channel (bot is in the channel)
                    chat = message.chat
                    channel_id = str(chat.id)
                    channel_name = chat.title
                    channel_type = chat.type
                    
                    # Add channel to configuration
                    self.channels[channel_id] = {
                        "name": channel_name,
                        "type": channel_type,
                        "username": chat.username
                    }
                    self.save_channels()
                    
                    keyboard = [[InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await message.reply_text(
                        f"✅ **Channel Added**\n\n"
                        f"**Name:** {channel_name}\n"
                        f"**ID:** `{channel_id}`\n"
                        f"**Type:** {channel_type}\n\n"
                        f"Channel has been added successfully!",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                else:
                    await message.reply_text(
                        "❌ **Invalid Message**\n\n"
                        "Please send:\n"
                        "• A forwarded message from the channel\n"
                        "• Channel username (e.g., @channelname)\n"
                        "• Channel ID (e.g., -1001234567890)\n\n"
                        "**For private channels:** Forward any message from the channel to this chat."
                    )
                
        except Exception as e:
            await message.reply_text(f"❌ **Error**\n\nFailed to add channel: {e}")
            
    async def handle_join_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle join requests - auto approve and send welcome message"""
        join_request = update.chat_join_request
        user = join_request.from_user
        chat = join_request.chat
        
        # Auto-approve the join request
        try:
            await join_request.approve()
            logger.info(f"Approved join request from {user.username} ({user.id}) in {chat.title}")
        except Exception as e:
            logger.error(f"Failed to approve join request: {e}")
            return
            
        # Send welcome message via DM
        dm_sent = False
        error_msg = None
        
        try:
            # Check for channel-specific welcome message first
            channel_id = str(chat.id)
            channel_welcome = None
            
            if channel_id in self.channel_messages and "welcome" in self.channel_messages[channel_id]:
                channel_welcome = self.channel_messages[channel_id]["welcome"]
                await self.send_message_by_type(context, user.id, channel_welcome)
                logger.info(f"Channel-specific welcome message sent to {user.username} ({user.id}) from {chat.title}")
            elif self.welcome_message_data:
                # Fallback to global welcome message
                await self.send_message_by_type(context, user.id, self.welcome_message_data)
                logger.info(f"Global welcome message sent to {user.username} ({user.id})")
            else:
                # Fallback to default text message
                await context.bot.send_message(
                    chat_id=user.id,
                    text=DEFAULT_WELCOME
                )
                logger.info(f"Default welcome message sent to {user.username} ({user.id})")
                
            dm_sent = True
        except Exception as e:
            error_msg = str(e)
            logger.warning(f"Failed to send welcome message to {user.username} ({user.id}): {e}")
            
        # Log the join
        self.log_join(
            username=user.username or "Unknown",
            user_id=user.id,
            dm_sent=dm_sent,
            error=error_msg
        )
        
    async def handle_new_chat_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle when bot is added to a channel/group"""
        message = update.message
        chat = message.chat
        
        # Check if the bot was added
        for new_member in message.new_chat_members:
            if new_member.id == context.bot.id:
                # Bot was added to this chat
                if chat.type in ['channel', 'supergroup', 'group']:
                    # Get the user who added the bot
                    added_by = message.from_user
                    
                    # Check if the user is an admin
                    if added_by.id in self.admins:
                        chat_type = "Channel" if chat.type == "channel" else "Supergroup" if chat.type == "supergroup" else "Group"
                        username_info = f"\n**Username:** @{chat.username}" if chat.username else "\n**Username:** None (Private)"
                        
                        # Send channel info to the admin
                        await context.bot.send_message(
                            chat_id=added_by.id,
                            text=f"🎉 **Bot Added Successfully!**\n\n"
                                 f"**Chat Information:**\n"
                                 f"**Type:** {chat_type}\n"
                                 f"**Title:** {chat.title}\n"
                                 f"**ID:** `{chat.id}`\n"
                                 f"{username_info}\n\n"
                                 f"**To add this to your bot:**\n"
                                 f"1. Copy the ID: `{chat.id}`\n"
                                 f"2. Send `/admin` to your bot\n"
                                 f"3. Click '📢 Manage Channels'\n"
                                 f"4. Click '➕ Add Channel'\n"
                                 f"5. Paste the ID: `{chat.id}`\n\n"
                                 f"**Note:** The bot will now automatically approve join requests in this chat!",
                            parse_mode='Markdown'
                        )
                        
                        # Also send a message in the channel/group
                        await message.reply_text(
                            f"✅ **Bot Activated!**\n\n"
                            f"**Channel ID:** `{chat.id}`\n\n"
                            f"This bot will now:\n"
                            f"• ✅ Auto-approve join requests\n"
                            f"• ✅ Send welcome messages to new members\n"
                            f"• ✅ Send scheduled messages (if configured)\n\n"
                            f"**Admin:** Use `/admin` in private chat to configure the bot.",
                            parse_mode='Markdown'
                        )
                    else:
                        # Non-admin added the bot
                        await message.reply_text(
                            "❌ **Access Denied**\n\n"
                            "Only authorized admins can add this bot to channels/groups.\n"
                            "Please contact the bot administrator."
                        )
                break
        
    async def send_message_by_type(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_data: dict):
        """Send message based on its type (text, photo, video, voice, etc.)"""
        if not message_data:
            return
            
        message_type = message_data.get("type")
        file_id = message_data.get("file_id")
        content = message_data.get("content")
        caption = message_data.get("caption")
        
        try:
            if message_type == "text":
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=content,
                    caption=caption
                )
            elif message_type == "photo":
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=file_id,
                    caption=caption
                )
            elif message_type == "video":
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=file_id,
                    caption=caption
                )
            elif message_type == "voice":
                await context.bot.send_voice(
                    chat_id=chat_id,
                    voice=file_id,
                    caption=caption
                )
            elif message_type == "audio":
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=file_id,
                    caption=caption
                )
            elif message_type == "document":
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=file_id,
                    caption=caption
                )
            elif message_type == "video_note":
                await context.bot.send_video_note(
                    chat_id=chat_id,
                    video_note=file_id
                )
            else:
                # Fallback to text
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=content or "Message sent"
                )
        except Exception as e:
            logger.error(f"Failed to send {message_type} message: {e}")
            # Fallback to text message
            await context.bot.send_message(
                chat_id=chat_id,
                text=content or "Welcome message"
            )
            
    async def show_channel_management(self, query):
        """Show channel management options"""
        keyboard = [
            [
                InlineKeyboardButton("📋 List Channels", callback_data="list_channels"),
                InlineKeyboardButton("➕ Add Channel", callback_data="add_channel")
            ],
            [
                InlineKeyboardButton("🗑️ Remove Channel", callback_data="remove_channel"),
                InlineKeyboardButton("🔙 Back", callback_data="back_to_admin")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📢 **Channel Management**\n\nManage channels for welcome and scheduled messages.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    async def list_channels(self, query):
        """List all configured channels"""
        if not self.channels:
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="manage_channels")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "📋 **No Channels Configured**\n\nNo channels have been added yet.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
            
        channels_text = "📋 **Configured Channels:**\n\n"
        for channel_id, channel_info in self.channels.items():
            channels_text += f"• **{channel_info['name']}**\n"
            channels_text += f"  ID: `{channel_id}`\n"
            channels_text += f"  Type: {channel_info['type']}\n\n"
            
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="manage_channels")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            channels_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    async def show_channel_removal(self, query):
        """Show channel removal options"""
        if not self.channels:
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="manage_channels")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🗑️ **No Channels to Remove**\n\nNo channels have been configured.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
            
        keyboard = []
        for channel_id, channel_info in self.channels.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"🗑️ {channel_info['name']}", 
                    callback_data=f"remove_channel_{channel_id}"
                )
            ])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="manage_channels")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🗑️ **Remove Channel**\n\nSelect a channel to remove:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    async def show_channel_messages_menu(self, query):
        """Show channel-specific messages menu"""
        if not self.channels:
            keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_admin")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🎯 **Channel Messages**\n\n❌ No channels configured yet!\n\nPlease add channels first using '📢 Manage Channels'.",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
            return
            
        # Show channels with their message status
        channels_text = "🎯 **Channel-Specific Messages**\n\n"
        keyboard = []
        
        for channel_id, channel_info in self.channels.items():
            has_welcome = "✅" if channel_id in self.channel_messages and "welcome" in self.channel_messages[channel_id] else "❌"
            has_schedule = "✅" if channel_id in self.channel_messages and "schedule" in self.channel_messages[channel_id] else "❌"
            
            channels_text += f"📢 **{channel_info['name']}**\n"
            channels_text += f"   Welcome: {has_welcome} | Schedule: {has_schedule}\n\n"
            
            # Add buttons for this channel
            keyboard.append([
                InlineKeyboardButton(
                    f"📩 {channel_info['name']} Welcome", 
                    callback_data=f"channel_welcome_{channel_id}"
                )
            ])
            keyboard.append([
                InlineKeyboardButton(
                    f"🕒 {channel_info['name']} Schedule", 
                    callback_data=f"channel_schedule_{channel_id}"
                )
            ])
        
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="back_to_admin")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            channels_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    async def send_scheduled_message(self):
        """Send scheduled message to all configured channels"""
        logger.info(f"Sending scheduled messages to {len(self.channels)} channels")
        
        # Send to all configured channels
        for channel_id in self.channels:
            try:
                # Check for channel-specific scheduled message first
                channel_schedule = None
                if channel_id in self.channel_messages and "schedule" in self.channel_messages[channel_id]:
                    channel_schedule = self.channel_messages[channel_id]["schedule"]
                    await self.send_message_by_type(self.application.bot, int(channel_id), channel_schedule)
                    logger.info(f"Channel-specific scheduled message sent to channel {channel_id}")
                elif self.scheduled_message_data:
                    # Fallback to global scheduled message
                    await self.send_message_by_type(self.application.bot, int(channel_id), self.scheduled_message_data)
                    logger.info(f"Global scheduled message sent to channel {channel_id}")
                else:
                    logger.warning(f"No scheduled message configured for channel {channel_id}")
                    
            except Exception as e:
                logger.error(f"Failed to send scheduled message to channel {channel_id}: {e}")
        
    def run(self):
        """Start the bot"""
        logger.info("Starting bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main function"""
    # Get bot token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        print("Please set your bot token as an environment variable.")
        return
        
    # Create and run bot
    bot = TelegramBot(token)
    bot.run()

if __name__ == "__main__":
    main()
