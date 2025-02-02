import os
import json
import base64
import firebase_admin
from firebase_admin import credentials, firestore
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Load Firebase credentials from environment variable
firebase_json = os.getenv("FIREBASE_CREDENTIALS")

if firebase_json:
    decoded_json = base64.b64decode(firebase_json).decode('utf-8')
    cred_dict = json.loads(decoded_json)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    raise ValueError("🔥 FIREBASE_CREDENTIALS environment variable is missing!")

# Telegram Bot Token from Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TELEGRAM_TOKEN:
    raise ValueError("🤖 TELEGRAM_BOT_TOKEN is missing in environment variables!")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Use /track <product_url> to track a price.")

# Track price command (Placeholder Function)
async def track(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Your product is now being tracked!")

# Main function to start bot
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("track", track))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()