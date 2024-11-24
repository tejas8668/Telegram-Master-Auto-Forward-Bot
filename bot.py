#    Copyright (c) 2021 Ayush
#    
#    This program is free software: you can redistribute it and/or modify  
#    it under the terms of the GNU General Public License as published by  
#    the Free Software Foundation, version 3.
# 
#    This program is distributed in the hope that it will be useful, but 
#    WITHOUT ANY WARRANTY; without even the implied warranty of 
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
#    General Public License for more details.
# 
#    License can be found in < https://github.com/Ayush7445/telegram-auto_forwarder/blob/main/License > .

from pyrogram import Client, filters
from decouple import config
import logging

# Configure logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

# Print starting message
print("Starting...")

# Read configuration from environment variables
API_ID = config("API_ID", cast=int)
API_HASH = config("API_HASH")
SESSION_STRING = config("SESSION_STRING")
FROM_CHANNELS = config("FROM_CHANNEL", cast=lambda x: [int(i.strip()) for i in x.split(',')])
TO_CHANNELS = config("TO_CHANNEL", cast=lambda x: [int(i.strip()) for i in x.split(',')])
BLOCKED_TEXTS = config("BLOCKED_TEXTS", cast=lambda x: [i.strip().lower() for i in x.split(',')])
MEDIA_FORWARD_RESPONSE = config("MEDIA_FORWARD_RESPONSE", default="yes").lower()
YOUR_ADMIN_USER_ID = config("YOUR_ADMIN_USER_ID", cast=int)
BOT_API_KEY = config("BOT_API_KEY", default="", cast=str)

# Initialize Pyrogram client with session string
app = Client("my_bot", session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH, bot_token=BOT_API_KEY)

# Handler for the /start command
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(f"Hello {message.from_user.first_name}! Welcome to the Telegram Forwarding Bot. I'm here to help you forward messages.")

# Handler for the /help command
@app.on_message(filters.command("help"))
async def help(client, message):
    help_text = "This bot forwards messages from specified channels to other channels. Configure the bot using the following environment variables:\n"
    help_text += "1. API_ID: Your API ID\n"
    help_text += "2. API_HASH: Your API Hash\n"
    help_text += "3. SESSION_STRING: Your session string\n"
    help_text += "4. FROM_CHANNEL: Comma-separated list of channel IDs to forward from\n"
    help_text += "5. TO_CHANNEL: Comma-separated list of channel IDs to forward to\n"
    help_text += "6. BLOCKED_TEXTS: Comma-separated list of texts to block\n"
    help_text += "7. MEDIA_FORWARD_RESPONSE: 'yes' to forward media, 'no' to skip\n"
    help_text += "8. YOUR_ADMIN_USER_ID: Your admin user ID\n"
    help_text += "9. BOT_API_KEY: Your bot API key\n"
    await message.reply_text(help_text)

# Event handler for incoming messages
@app.on_message(filters.chat(FROM_CHANNELS))
async def forward_messages(client, message):
    try:
        message_text = message.text.lower() if message.text else ""

        if any(blocked_text in message_text for blocked_text in BLOCKED_TEXTS):
            print(f"Blocked message containing one of the specified texts: {message_text}")
            logging.warning(f"Blocked message containing one of the specified texts: {message_text}")
            return

        if message.media and MEDIA_FORWARD_RESPONSE == 'yes':
            for to_channel in TO_CHANNELS:
                await client.send_message(chat_id=to_channel, text=message_text, file=message.document.file_id if message.document else None)
                print(f"Forwarded media message to channel {to_channel}")
        else:
            for to_channel in TO_CHANNELS:
                await client.send_message(chat_id=to_channel, text=message_text)
                print(f"Forwarded text message to channel {to_channel}")

    except Exception as e:
        print(f"Error forwarding message: {e}")

# Run the bot
print("Bot has started.")
app.run()
