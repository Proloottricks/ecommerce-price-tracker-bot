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
from pymongo import MongoClient
from bs4 import BeautifulSoup
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# =====================
# HEALTH CHECK SERVER
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

def run_health_check():
    health_app.run(host='0.0.0.0', port=8080, use_reloader=False)

# =====================
# PRICE TRACKING FUNCTIONS
# =====================
def scrape_price(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
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

def generate_affiliate_link(url):
    if "amazon" in url:
        return f"{url}?tag={os.getenv('AMAZON_AFFILIATE_ID')}"
    elif "flipkart" in url:
        return f"{url}&affid={os.getenv('FLIPKART_AFFILIATE_ID')}"
    return url

# =====================
# TELEGRAM BOT
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛒 Price Tracker Bot Ready!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    user_id = update.message.from_user.id
    
    if any(domain in url for domain in ["amazon", "flipkart"]):
        price = scrape_price(url)
        if price:
            affiliate_link = generate_affiliate_link(url)
            
            # Save to MongoDB (simplified)
            MongoClient(os.getenv("MONGO_URI")).PriceTracker.products.update_one(
                {"url": url},
                {"$set": {
                    "price": price,
                    "affiliate_link": affiliate_link,
                    "last_checked": time.time()
                }},
                upsert=True
            )
            
            await update.message.reply_text(
                f"✅ Tracking Started!\nPrice: ₹{price}\n[Buy Now]({affiliate_link})",
                parse_mode="Markdown"
            )

def run_bot():
    application = Application.builder() \
        .token(os.getenv("TELEGRAM_TOKEN")) \
        .build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    application.run_polling()

# =====================
# MAIN EXECUTION
# =====================
if __name__ == "__main__":
    # Start health check
    threading.Thread(target=run_health_check, daemon=True).start()
    
    # Start bot with auto-restart
    while True:
        try:
            run_bot()
        except Exception as e:
            print(f"Bot crashed: {e}")
            time.sleep(5)