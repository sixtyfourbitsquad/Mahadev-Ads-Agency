import os
import json
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters, ChatJoinRequestHandler
)
# Removed scheduler import - no more scheduled messaging

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
        
        # No more scheduler - removed scheduled messaging
        
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
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
            
    def save_welcome_data(self):
        """Save welcome message data to JSON file"""
        if self.welcome_message_data:
            with open("welcome_data.json", 'w') as f:
                json.dump(self.welcome_message_data, f)
                
    # Removed scheduled message functionality
                
    def save_channels(self):
        """Save channels to JSON file"""
        with open(self.CHANNELS_FILE, 'w') as f:
            json.dump(self.channels, f)
            
    def save_admins(self):
        """Save admins to JSON file"""
        with open(self.ADMINS_FILE, 'w') as f:
            json.dump(self.admins, f)
            
    def save_welcome(self):
        """Save welcome message to file"""
        with open(self.WELCOME_FILE, 'w') as f:
            f.write(self.welcome_message)
            
    def save_users(self):
        """Save users to file (NEW)"""
        with open(self.USERS_FILE, 'w') as f:
            json.dump(self.users, f, indent=2)
            
    async def save_message_by_type(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_type: str):
        """Save message data based on type"""
        message = update.message
        
        if message.text:
            # Text message
            message_data = {
                "type": "text",
                "content": message.text
            }
        elif message.photo:
            # Photo message
            message_data = {
                "type": "photo",
                "file_id": message.photo[-1].file_id,
                "caption": message.caption
            }
        elif message.video:
            # Video message
            message_data = {
                "type": "video",
                "file_id": message.video.file_id,
                "caption": message.caption
            }
        elif message.voice:
            # Voice message
            message_data = {
                "type": "voice",
                "file_id": message.voice.file_id
            }
        elif message.audio:
            # Audio message
            message_data = {
                "type": "audio",
                "file_id": message.audio.file_id,
                "caption": message.caption
            }
        elif message.document:
            # Document message
            message_data = {
                "type": "document",
                "file_id": message.document.file_id,
                "caption": message.caption
            }
        elif message.video_note:
            # Video note message
            message_data = {
                "type": "video_note",
                "file_id": message.video_note.file_id
            }
        else:
            await message.reply_text("❌ Unsupported message type. Please send text, photo, video, voice, audio, document, or video note.")
            return
            
        # Save message data
        if message_type == "welcome":
            self.welcome_message_data = message_data
            self.save_welcome_data()
            await message.reply_text("✅ Welcome message saved successfully!")
        elif message_type == "broadcast":
            # NEW: Save broadcast message and send to all users
            await self.broadcast_message_to_all_users(message, message_data, context)
            
        # Clear admin state
        user_id = update.effective_user.id
        if user_id in self.admin_states:
            del self.admin_states[user_id]
            
    def log_join(self, username: str, user_id: int, dm_sent: bool, error: str = None):
        """Log join request details"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "✅ DM Sent" if dm_sent else "❌ DM Failed"
        error_info = f" (Error: {error})" if error else ""
        
        log_entry = f"[{timestamp}] @{username} (ID: {user_id}) - {status}{error_info}\n"
        
        with open(self.LOGS_FILE, 'a') as f:
            f.write(log_entry)
            
    async def broadcast_message_to_all_users(self, message, message_data, context):
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
        
        # Store user information (NEW) - but not admin users
        if str(user.id) not in self.users and user.id not in self.admins:
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
            
        # Removed scheduled messaging functionality
            
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
            
        # Removed interval handling - no more scheduled messaging
            
        elif data.startswith("remove_"):
            channel_id = data.split("_")[1]
            if channel_id in self.channels:
                channel_name = self.channels[channel_id]["name"]
                del self.channels[channel_id]
                self.save_channels()
                await query.edit_message_text(f"✅ Channel '{channel_name}' removed successfully!")
            else:
                await query.edit_message_text("❌ Channel not found!")
    # Removed scheduled messaging methods
    async def show_logs(self, query):
        """Show recent logs"""
        try:
            with open(self.LOGS_FILE, 'r') as f:
                logs = f.read()
                
            if logs:
                # Show last 10 lines
                lines = logs.strip().split('\n')[-10:]
                log_text = '\n'.join(lines)
                
                await query.edit_message_text(
                    f"📑 **Recent Logs**\n\n"
                    f"```\n{log_text}\n```",
                    parse_mode='Markdown'
                )
            else:
                await query.edit_message_text("📑 **Recent Logs**\n\nNo logs available yet.")
        except FileNotFoundError:
            await query.edit_message_text("📑 **Recent Logs**\n\nNo logs file found.")
            
    async def stop_bot(self, query):
        """Stop the bot"""
        await query.edit_message_text("🛑 Bot is stopping...")
        await self.application.stop()
        
    async def show_admin_panel_from_query(self, query, context):
        """Show admin panel from callback query"""
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
        await query.edit_message_text(
            "🔧 **Admin Panel**\n\n"
            "Welcome to the admin panel. Use the buttons below to manage the bot:",
            reply_markup=reply_markup
        )
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages for admin responses"""
        if not update.effective_user:
            return
            
        user_id = update.effective_user.id
        
        if user_id not in self.admins:
            return
            
        if user_id not in self.admin_states:
            return
            
        state = self.admin_states[user_id]
        
        if state == "waiting_welcome":
            await self.save_message_by_type(update, context, "welcome")
            
        elif state == "waiting_broadcast":
            await self.save_message_by_type(update, context, "broadcast")
            
        elif state == "waiting_channel":
            await self.handle_channel_addition(update, context)
            
    async def handle_channel_addition(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle channel addition process"""
        message = update.message
        user_id = update.effective_user.id
        
        try:
            # Check if it's a forwarded message from a channel
            if hasattr(message, 'forward_from_chat') and message.forward_from_chat and message.forward_from_chat.type in ['channel', 'supergroup']:
                chat = message.forward_from_chat
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
                    f"✅ **Channel Added Successfully!**\n\n"
                    f"**Name:** {channel_name}\n"
                    f"**Type:** {channel_type.title()}\n"
                    f"**ID:** `{channel_id}`\n"
                    f"**Username:** @{chat.username if chat.username else 'None (Private)'}\n\n"
                    f"The bot will now send welcome and scheduled messages to this channel.",
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
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
                        f"✅ **Channel Added Successfully!**\n\n"
                        f"**Name:** {channel_name}\n"
                        f"**Type:** {channel_type.title()}\n"
                        f"**ID:** `{channel_id}`\n"
                        f"**Username:** @{chat.username if chat.username else 'None (Private)'}\n\n"
                        f"The bot will now send welcome and scheduled messages to this channel.",
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    
                else:
                    # Check if it's a username or ID
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
                                    f"✅ **Channel Added Successfully!**\n\n"
                                    f"**Name:** {channel_name}\n"
                                    f"**Type:** {channel_type.title()}\n"
                                    f"**ID:** `{channel_id}`\n"
                                    f"**Username:** @{username}\n\n"
                                    f"The bot will now send welcome and scheduled messages to this channel.",
                                    reply_markup=reply_markup,
                                    parse_mode='Markdown'
                                )
                            else:
                                await message.reply_text("❌ **Error**\n\nThis is not a channel or supergroup.")
                        except Exception as e:
                            await message.reply_text(f"❌ **Error**\n\nCould not find channel with username @{username}")
                            
                    elif text.startswith('-100'):
                        # Channel ID format
                        try:
                            chat = await context.bot.get_chat(int(text))
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
                                    f"✅ **Channel Added Successfully!**\n\n"
                                    f"**Name:** {channel_name}\n"
                                    f"**Type:** {channel_type.title()}\n"
                                    f"**ID:** `{channel_id}`\n"
                                    f"**Username:** @{chat.username if chat.username else 'None (Private)'}\n\n"
                                    f"The bot will now send welcome and scheduled messages to this channel.",
                                    reply_markup=reply_markup,
                                    parse_mode='Markdown'
                                )
                            else:
                                await message.reply_text("❌ **Error**\n\nThis is not a channel or supergroup.")
                        except Exception as e:
                            await message.reply_text(f"❌ **Error**\n\nCould not find channel with ID {text}")
                            
                    else:
                        await message.reply_text(
                            "❌ **Invalid Message**\n\n"
                            "Please send a forwarded message from the channel or the channel username/ID."
                        )
                        
        except Exception as e:
            await message.reply_text(f"❌ **Error**\n\nFailed to add channel: {str(e)}")
            
        # Clear admin state
        if user_id in self.admin_states:
            del self.admin_states[user_id]
            
    async def handle_join_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle join requests - automatically approve and send welcome message"""
        join_request = update.chat_join_request
        user = join_request.from_user
        chat = join_request.chat
        
        # Automatically approve the request
        try:
            await join_request.approve()
            dm_sent = False
            error_msg = None
            
            # Try to send welcome message via DM
            if self.welcome_message_data:
                try:
                    await self.send_message_by_type(context, user.id, self.welcome_message_data)
                    dm_sent = True
                except Exception as e:
                    error_msg = str(e)
                    
            # Log the join
            self.log_join(
                username=user.username or "Unknown",
                user_id=user.id,
                dm_sent=dm_sent,
                error=error_msg
            )
            
        except Exception as e:
            # Log the error
            self.log_join(
                username=user.username or "Unknown",
                user_id=user.id,
                dm_sent=False,
                error=f"Failed to approve: {str(e)}"
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
                    
                    # Send channel info to the admin
                    chat_type = "Channel" if chat.type == "channel" else "Supergroup" if chat.type == "supergroup" else "Group"
                    username_info = f"\n**Username:** @{chat.username}" if chat.username else "\n**Username:** None (Private)"
                    
                    try:
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
                                 f"**Note:** The bot is now ready to handle join requests and send messages to this chat!",
                            parse_mode='Markdown'
                        )
                    except Exception as e:
                        # If we can't send DM, log it
                        self.log_join(
                            username=added_by.username or "Unknown",
                            user_id=added_by.id,
                            dm_sent=False,
                            error=f"Could not send channel info DM: {str(e)}"
                        )
                        
    async def send_message_by_type(self, context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_data: dict):
        """Send message based on type"""
        if not message_data:
            return
            
        message_type = message_data.get("type")
        
        try:
            if message_type == "text":
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message_data["content"]
                )
            elif message_type == "photo":
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=message_data["file_id"],
                    caption=message_data.get("caption")
                )
            elif message_type == "video":
                await context.bot.send_video(
                    chat_id=chat_id,
                    video=message_data["file_id"],
                    caption=message_data.get("caption")
                )
            elif message_type == "voice":
                await context.bot.send_voice(
                    chat_id=chat_id,
                    voice=message_data["file_id"]
                )
            elif message_type == "audio":
                await context.bot.send_audio(
                    chat_id=chat_id,
                    audio=message_data["file_id"],
                    caption=message_data.get("caption")
                )
            elif message_type == "document":
                await context.bot.send_document(
                    chat_id=chat_id,
                    document=message_data["file_id"],
                    caption=message_data.get("caption")
                )
            elif message_type == "video_note":
                await context.bot.send_video_note(
                    chat_id=chat_id,
                    video_note=message_data["file_id"]
                )
        except Exception as e:
            logger.error(f"Failed to send {message_type} message: {str(e)}")
            
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
                InlineKeyboardButton("🗑️ Remove Channel", callback_data="remove_channel")
            ],
            [
                InlineKeyboardButton("🔙 Back to Admin Panel", callback_data="back_to_admin")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "📢 **Channel Management**\n\n"
            "Manage channels for welcome messages:",
            reply_markup=reply_markup
        )
        
    async def list_channels(self, query):
        """List all configured channels"""
        if not self.channels:
            keyboard = [[InlineKeyboardButton("🔙 Back to Channel Management", callback_data="manage_channels")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "📋 **Configured Channels**\n\n"
                "No channels configured yet.\n\n"
                "Use '➕ Add Channel' to add your first channel.",
                reply_markup=reply_markup
            )
            return
            
        channels_text = "📋 **Configured Channels**\n\n"
        for channel_id, channel_info in self.channels.items():
            channels_text += f"**{channel_info['name']}**\n"
            channels_text += f"• Type: {channel_info['type'].title()}\n"
            channels_text += f"• ID: `{channel_id}`\n"
            channels_text += f"• Username: @{channel_info['username'] if channel_info['username'] else 'None (Private)'}\n\n"
            
        keyboard = [[InlineKeyboardButton("🔙 Back to Channel Management", callback_data="manage_channels")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            channels_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
    async def show_channel_removal(self, query):
        """Show channel removal options"""
        if not self.channels:
            keyboard = [[InlineKeyboardButton("🔙 Back to Channel Management", callback_data="manage_channels")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "🗑️ **Remove Channel**\n\n"
                "No channels configured to remove.",
                reply_markup=reply_markup
            )
            return
            
        keyboard = []
        for channel_id, channel_info in self.channels.items():
            keyboard.append([
                InlineKeyboardButton(
                    f"🗑️ {channel_info['name']}",
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
        
    # Removed scheduled messaging functionality
                
    def run(self):
        """Run the bot"""
        self.application.run_polling()
        
def main():
    """Main function"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment variables")
        return
        
    print("🚀 Starting bot...")
    bot = TelegramBot(token)
    bot.run()
    
if __name__ == "__main__":
    main()
