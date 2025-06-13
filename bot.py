import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment Variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
SOURCE_CHANNEL_ID = -100483873372772
TARGET_CHANNEL_ID = -100578376883737
SHORTLINK_API = os.environ.get("SHORTLINK_API")
SHORTLINK_URL = os.environ.get("SHORTLINK_URL")

# Handler Function
async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post
    if not message:
        return

    media = message.document or message.video or message.audio or message.photo[-1]
    file_name = getattr(media, 'file_name', 'media_file')

    telegram_file = await media.get_file()
    local_path = await telegram_file.download_to_drive()
    logger.info(f"Downloaded: {local_path}")

    # Upload to Gofile WITHOUT API Key
    with open(local_path, 'rb') as f:
        files = {'file': (file_name, f)}
        res = requests.post("https://api.gofile.io/uploadFile", files=files)
        data = res.json()

    if data['status'] == 'ok':
        gofile_link = data['data']['downloadPage']
        logger.info(f"Gofile Link: {gofile_link}")

        # Shortlink if available
        try:
            short_res = requests.get(SHORTLINK_API + gofile_link)
            short_url = short_res.text.strip()
        except Exception as e:
            logger.warning(f"Shortlink failed: {e}")
            short_url = gofile_link

        caption = f"📁 <b>{file_name}</b>\n🔗 <a href='{short_url}'>Download Link</a>"
        thumb = local_path if message.photo or message.video else None

        await context.bot.send_photo(
            chat_id=TARGET_CHANNEL_ID,
            photo=thumb,
            caption=caption,
            parse_mode='HTML'
        )
    else:
        logger.error("Gofile upload failed")

# Optional web server for Koyeb port fix
import threading
from fastapi import FastAPI
import uvicorn

def start_web():
    app = FastAPI()

    @app.get("/")
    def read_root():
        return {"status": "Bot is running"}

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)

threading.Thread(target=start_web).start()

# Main Bot Start
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.Chat(SOURCE_CHANNEL_ID) & filters.ALL, handle_channel_post))
    app.run_polling()
