import os
import atexit
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackContext
)
from pymongo import MongoClient
from database import add_product, get_user_products, stop_tracking
from scraper import scrape_price
from utils import generate_affiliate_link
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# MongoDB Connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client["PriceTrackerDB"]
products = db["products"]

# Cleanup function
@atexit.register
def cleanup():
    client.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛒 Price Tracker Bot\n\n"
        "Send me product links from Amazon/Flipkart/Ajio/Shopsy to track prices!"
    )

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

def main():
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == "__main__":
    main()