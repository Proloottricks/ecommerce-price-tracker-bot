import os
import time
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from database import add_product, get_user_products, stop_tracking
from scraper import scrape_price
from utils import generate_affiliate_link
from dotenv import load_dotenv

load_dotenv()

# Health Check Server Setup
app = Flask(__name__)

@app.route('/')
def health_check():
    try:
        # Test MongoDB connection if enabled
        if os.getenv("MONGO_URI"):
            from pymongo import MongoClient
            MongoClient(os.getenv("MONGO_URI")).admin.command('ping')
        return "✅ Bot is Healthy", 200
    except Exception as e:
        return f"⚠️ Degraded: {str(e)}", 500

def run_flask():
    app.run(host='0.0.0.0', port=8080, use_reloader=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛒 Price Tracker Bot is Active!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_id = update.message.from_user.id
    
    if any(domain in url for domain in ["amazon", "flipkart", "ajio", "shopsy"]):
        price = scrape_price(url)
        if price:
            affiliate_link = generate_affiliate_link(url)
            add_product(user_id, url, price, affiliate_link)
            
            keyboard = [
                [InlineKeyboardButton("🛒 Buy Now", url=affiliate_link)],
                [InlineKeyboardButton("❌ Stop Tracking", callback_data=f"stop_{url}")]
            ]
            
            await update.message.reply_text(
                f"✅ Tracking Started!\n\n"
                f"💰 Current Price: ₹{price}\n"
                f"🔗 [Product Link]({affiliate_link})",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

def run_bot():
    application = Application.builder() \
        .token(os.getenv("TELEGRAM_TOKEN")) \
        .build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == "__main__":
    # Start health check server
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Start bot with auto-restart
    while True:
        try:
            print("Starting bot...")
            run_bot()
        except Exception as e:
            print(f"Bot error: {e}")
            print("Restarting in 5 seconds...")
            time.sleep(5)