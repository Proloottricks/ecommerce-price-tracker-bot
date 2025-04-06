import os
import asyncio
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
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

load_dotenv()

# =====================
# PRODUCTION HEALTH CHECK
# =====================
health_app = Flask(__name__)

@health_app.route('/')
def health_check():
    try:
        # Test MongoDB connection
        MongoClient(os.getenv("MONGO_URI"), serverSelectionTimeoutMS=2000).admin.command('ping')
        return "✅ Bot & DB Active", 200
    except Exception as e:
        return f"⚠️ Service Issue: {str(e)}", 500

def run_health_server():
    from waitress import serve
    serve(health_app, host="0.0.0.0", port=8080)

# =====================
# BOT FUNCTIONS (ASYNCIO)
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛒 Price Tracker Bot Ready!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if any(domain in url for domain in ["amazon", "flipkart"]):
        price = await scrape_price(url)
        if price:
            affiliate_link = generate_affiliate_link(url)
            await save_to_db(url, price, affiliate_link)
            await update.message.reply_text(
                f"✅ Tracking Started!\nPrice: ₹{price}\n[Buy Now]({affiliate_link})",
                parse_mode="Markdown"
            )

async def scrape_price(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        async with requests.Session() as session:
            response = await session.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            if "amazon" in url:
                price = soup.find("span", class_="a-price-whole")
                return float(price.text.replace(",", "")) if price else None
            elif "flipkart" in url:
                price = soup.find("div", class_="_30jeq3")
                return float(price.text.replace("₹", "").replace(",", "")) if price else None
    except Exception as e:
        print(f"Scraping error: {e}")
        return None

async def save_to_db(url, price, affiliate_link):
    try:
        client = MongoClient(os.getenv("MONGO_URI"))
        client.PriceTracker.products.update_one(
            {"url": url},
            {"$set": {
                "price": price,
                "affiliate_link": affiliate_link,
                "last_checked": time.time()
            }},
            upsert=True
        )
    except Exception as e:
        print(f"DB error: {e}")

# =====================
# MAIN EXECUTION
# =====================
def run_bot():
    application = Application.builder() \
        .token(os.getenv("TELEGRAM_TOKEN")) \
        .build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    asyncio.run(application.run_polling())

if __name__ == "__main__":
    # Start production health server
    health_thread = threading.Thread(target=run_health_server)
    health_thread.daemon = True
    health_thread.start()

    # Start bot with proper asyncio handling
    while True:
        try:
            run_bot()
        except Exception as e:
            print(f"Bot error: {e}")
            time.sleep(5)