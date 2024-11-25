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
FROM_CHANNEL = config("FROM_CHANNEL", cast=lambda x: [int(i) for i in x.split()])
TO_CHANNEL = config("TO_CHANNEL", cast=lambda x: [int(i) for i in x.split()])
BLOCKED_TEXTS = config("BLOCKED_TEXTS", default="", cast=lambda x: [i.strip().lower() for i in x.split(',')])
MEDIA_FORWARD_RESPONSE = config("MEDIA_FORWARD_RESPONSE", default="yes").lower()

# Initialize Pyrogram client
app = Client("my_forwarder", session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)

# Forward function
@app.on_message(filters.chat(FROM_CHANNEL))
async def forward_message(client, message):
    try:
        # Check if the message contains blocked texts
        if message.text:
            message_text = message.text.lower()
            if any(blocked_text in message_text for blocked_text in BLOCKED_TEXTS):
                print(f"Blocked message containing one of the specified texts: {message.text}")
                logging.warning(f"Blocked message containing one of the specified texts: {message.text}")
                return
        
        # Forward messages to the destination channels
        for channel_id in TO_CHANNEL:
            if message.media and MEDIA_FORWARD_RESPONSE == "yes":
                await client.copy_message(chat_id=channel_id, from_chat_id=message.chat.id, message_id=message.message_id)
                print(f"Forwarded media message to channel {channel_id}")
            elif message.text:
                await client.send_message(chat_id=channel_id, text=message.text)
                print(f"Forwarded text message to channel {channel_id}")

    except Exception as e:
        print(f"Error forwarding message: {e}")
        logging.error(f"Error forwarding message: {e}")

# Run the bot
print("Bot has started.")
app.run()
