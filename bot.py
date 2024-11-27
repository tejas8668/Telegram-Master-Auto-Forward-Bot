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
BLOCKED_TEXTS = config("BLOCKED_TEXTS", default="", cast=lambda x: [i.strip().lower() for i in x.split(',')])
MEDIA_FORWARD_RESPONSE = config("MEDIA_FORWARD_RESPONSE", default="yes").lower()
YOUR_ADMIN_USER_ID = config("YOUR_ADMIN_USER_ID", default=0, cast=int)
BOT_API_KEY = config("BOT_API_KEY", default="", cast=str)

# Group-wise source and destination mapping
GROUPS = {
    "group_A": {
        "sources": [-1002305702191, -1002280468356],
        "destinations": [-1002377412867]
    },
    "group_B": {
        "sources": [-1002464896968],
        "destinations": [-1002377412867]
    },
    "group_C": {
        "sources": [-1002045849530],
        "destinations": [-1002377412867]
    },
    "group_D": {
        "sources": [-1001696674966],
        "destinations": [-1002325737859]
    }
}

# Flatten the list of all source channels for filtering
FROM_CHANNELS = [source for group in GROUPS.values() for source in group["sources"]]

# Initialize Pyrogram client
app = Client("my_forwarder", session_string=SESSION_STRING, api_id=API_ID, api_hash=API_HASH)

# Function to handle media messages
async def handle_media_message(client, message, channel_id):
    try:
        if message.photo:
            await client.send_photo(chat_id=channel_id, photo=message.photo.file_id, caption=message.caption)
        elif message.video:
            await client.send_video(chat_id=channel_id, video=message.video.file_id, caption=message.caption)
        elif message.document:
            await client.send_document(chat_id=channel_id, document=message.document.file_id, caption=message.caption)
        elif message.audio:
            await client.send_audio(chat_id=channel_id, audio=message.audio.file_id, caption=message.caption)
        elif message.voice:
            await client.send_voice(chat_id=channel_id, voice=message.voice.file_id, caption=message.caption)
        else:
            logging.warning("Unhandled media type.")
    except Exception as e:
        logging.error(f"Error handling media message: {e}")

# Forward function for messages from all source channels
@app.on_message(filters.chat(FROM_CHANNELS))
async def forward_message(client, message):
    try:
        # Add logging for message attributes
        logging.warning(f"Message attributes: {dir(message)}")

        # Check if the message contains blocked texts
        if message.text:
            message_text = message.text.lower()
            if any(blocked_text in message_text for blocked_text in BLOCKED_TEXTS):
                print(f"Blocked message containing one of the specified texts: {message.text}")
                logging.warning(f"Blocked message containing one of the specified texts: {message.text}")
                return

        # Determine destination channels for the source
        destination_channels = []
        for group in GROUPS.values():
            if message.chat.id in group["sources"]:
                destination_channels.extend(group["destinations"])

        # Copy messages to the respective destination channels
        for channel_id in destination_channels:
            if message.media and MEDIA_FORWARD_RESPONSE == "yes":
                await handle_media_message(client, message, channel_id)
                logging.info(f"Copied media message to channel {channel_id}")
            elif message.text:
                await client.send_message(chat_id=channel_id, text=message.text)
                logging.info(f"Copied text message to channel {channel_id}")

    except Exception as e:
        print(f"Error forwarding message: {e}")
        logging.error(f"Error forwarding message: {e}")

# Run the bot
print("Bot has started.")
app.run()
