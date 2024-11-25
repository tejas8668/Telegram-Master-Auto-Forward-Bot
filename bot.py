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

import logging
from pyrogram import Client, filters
from decouple import config

# Configure logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.WARNING)

# Print starting message
print("Starting...")

# Read configuration from environment variables
API_ID = config("API_ID", cast=int)
API_HASH = config("API_HASH")
SESSION_STRING = config("SESSION_STRING")
BLOCKED_TEXTS = config("BLOCKED_TEXTS", cast=lambda x: [i.strip().lower() for i in x.split(',')])
MEDIA_FORWARD_RESPONSE = config("MEDIA_FORWARD_RESPONSE", default="yes").lower()
YOUR_ADMIN_USER_ID = config("YOUR_ADMIN_USER_ID", cast=int)
BOT_API_KEY = config("BOT_API_KEY", default="", cast=str)

# Group-wise configuration
GROUPS = {
    "group_A": {
        "sources": ["-1002487065354"],
        "destinations": ["-1002325737859"]
    },
    "group_B": {
        "sources": ["-1002464896968"],
        "destinations": ["-1002299053628"]
    },
    "group_C": {
        "sources": ["-100237741286"],
        "destinations": ["-100220810990", "-100202962655"]
    },
    "group_D": {
        "sources": ["-10024028188893"],
        "destinations": ["-100222650665", "-100212975571"]
    }
}

# Flatten the sources list for easier filtering
FROM_CHANNELS = [source for group in GROUPS.values() for source in group["sources"]]

# Initialize Pyrogram client with session string
app = Client("my_user_account", session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)

# Handler for the /start command
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply_text(f"Hello {message.from_user.first_name}! Welcome to the Telegram Forwarding Bot. I'm here to help you forward messages.")

# Handler for the /help command
@app.on_message(filters.command("help"))
async def help(client, message):
    help_text = (
        "This bot forwards messages from specified groups to other groups based on your configuration. Configure the bot using the following environment variables:\n"
        "1. API_ID: Your API ID\n"
        "2. API_HASH: Your API Hash\n"
        "3. SESSION_STRING: Your session string\n"
        "4. GROUPS: Group-wise configuration with 'sources' and 'destinations'\n"
        "5. BLOCKED_TEXTS: Comma-separated list of texts to block\n"
        "6. MEDIA_FORWARD_RESPONSE: 'yes' to forward media, 'no' to skip\n"
        "7. YOUR ADMIN USER ID: Your admin user ID\n"
        "8. BOT_API_KEY: Your bot API key\n"
    )
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

        # Determine the target groups based on the source group
        for group_name, group in GROUPS.items():
            if str(message.chat.id) in group["sources"]:
                target_channels = group["destinations"]
                break
        else:
            target_channels = []

        if message.media and MEDIA_FORWARD_RESPONSE == 'yes':
            for to_channel in target_channels:
                await client.copy_message(chat_id=to_channel, from_chat_id=message.chat.id, message_id=message.message_id)
                print(f"Forwarded media message to channel {to_channel}")
        else:
            for to_channel in target_channels:
                await client.send_message(chat_id=to_channel, text=message.text if message.text else "")
                print(f"Forwarded text message to channel {to_channel}")

    except Exception as e:
        print(f"Error forwarding message: {e}")

# Run the bot
print("Bot has started.")
app.run()
