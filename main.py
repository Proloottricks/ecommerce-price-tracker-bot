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
    elif "flipkart" in url:
        price = soup.find("div", {"class": "_30jeq3"}).text
    elif "myntra" in url:
        price = soup.find("span", {"class": "p_price"}).text
    elif "ajio" in url:
        price = soup.find("span", {"class": "price"}).text
    else:
        price = "Site not supported"
    
    return price.strip()

def track_prices(context: CallbackContext):
    products = db.collection("tracked_products").get()
    for product in products:
        data = product.to_dict()
        url, user_id, target_price = data["url"], data["user_id"], data["target_price"]
        
        current_price = get_price(url)
        
        if current_price and float(current_price.replace(",", "")) <= target_price:
            context.bot.send_message(chat_id=user_id, text=f"Price dropped! {url}")
    
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
