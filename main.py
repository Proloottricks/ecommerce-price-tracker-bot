import os
import time
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import firebase_admin
from firebase_admin import credentials, firestore

# Firebase initialization
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Telegram bot token
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Send me a product link to track.")

def track(update: Update, context: CallbackContext):
    url = context.args[0]
    target_price = float(context.args[1])
    user_id = update.message.chat.id
    
    # Save product info to Firestore
    db.collection("tracked_products").add({
        "url": url,
        "target_price": target_price,
        "user_id": user_id
    })
    
    update.message.reply_text(f"Tracking {url} for price drops!")

def get_price(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    
    if "amazon" in url:
        price = soup.find("span", {"class": "a-price-whole"}).text
        affiliate_tag = os.getenv('AMAZON_AFFILIATE_TAG')
        affiliate_link = f"{url}?tag={affiliate_tag}"
    elif "flipkart" in url:
        price = soup.find("div", {"class": "_30jeq3"}).text
        affiliate_tag = os.getenv('FLIPKART_AFFILIATE_TAG')
        affiliate_link = f"{url}?affid={affiliate_tag}"
    elif "myntra" in url:
        price = soup.find("span", {"class": "p_price"}).text
        affiliate_tag = os.getenv('MYNTRA_AFFILIATE_TAG')
        affiliate_link = f"{url}?utm_source={affiliate_tag}"
    elif "ajio" in url:
        price = soup.find("span", {"class": "price"}).text
        affiliate_tag = os.getenv('AJIO_AFFILIATE_TAG')
        affiliate_link = f"{url}?utm_campaign={affiliate_tag}"
    else:
        price = "Site not supported"
        affiliate_link = url  # No affiliate tag for unsupported sites
    
    return price.strip(), affiliate_link

def track_prices(context: CallbackContext):
    products = db.collection("tracked_products").get()
    for product in products:
        data = product.to_dict()
        url, user_id, target_price = data["url"], data["user_id"], data["target_price"]
        
        current_price, affiliate_link = get_price(url)
        
        if current_price and float(current_price.replace(",", "")) <= target_price:
            context.bot.send_message(chat_id=user_id, text=f"Price dropped! {affiliate_link}")
    
    time.sleep(3600)  # Check price every hour

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("track", track))
    
    updater.job_queue.run_repeating(track_prices, interval=3600, first=0)
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
