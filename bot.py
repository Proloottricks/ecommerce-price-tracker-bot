import os
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from pymongo import MongoClient
from database import add_product, get_user_products, stop_tracking
from scraper import scrape_price
from utils import generate_affiliate_link
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# MongoDB Connection
MONGO_CLIENT = None

def get_mongo_client():
    global MONGO_CLIENT
    if MONGO_CLIENT is None:
        MONGO_CLIENT = MongoClient(os.getenv("MONGO_URI"))
    return MONGO_CLIENT

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛒 Price Tracker Bot\n\n"
        "Send me product links from Amazon/Flipkart/Ajio/Shopsy to track prices!"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        url = update.message.text
        user_id = update.message.from_user.id
        
        if any(domain in url for domain in ["amazon", "flipkart", "ajio", "shopsy"]):
            price = scrape_price(url)
            if price:
                db = get_mongo_client().PriceTrackerDB
                affiliate_link = generate_affiliate_link(url)
                
                db.products.update_one(
                    {"user_id": user_id, "url": url},
                    {"$set": {
                        "current_price": price,
                        "affiliate_link": affiliate_link,
                        "last_checked": datetime.now()
                    }},
                    upsert=True
                )
                
                await update.message.reply_text(
                    f"✅ Tracking Started!\n\n"
                    f"💰 Current Price: ₹{price}\n"
                    f"🔗 [Product Link]({affiliate_link})",
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🛒 Buy Now", url=affiliate_link)],
                        [InlineKeyboardButton("❌ Stop Tracking", callback_data=f"stop_{url}")]
                    ]),
                    parse_mode="Markdown"
                )
    except Exception as e:
        print(f"Error: {e}")

def main():
    application = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

if __name__ == "__main__":
    try:
        main()
    finally:
        if MONGO_CLIENT:
            MONGO_CLIENT.close()