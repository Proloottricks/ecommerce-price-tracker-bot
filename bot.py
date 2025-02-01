import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from tracker import fetch_price
from firebase_db import add_product, update_price
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Affiliate link conversion function
def convert_to_affiliate_link(url):
    if "amazon" in url:
        affiliate_id = "lootdealsrs0f-21"
        if "?" in url:
            url += f"&tag={affiliate_id}"
        else:
            url += f"?tag={affiliate_id}"
    elif "flipkart" in url:
        affiliate_id = "your_flipkart_affiliate_id"
        if "?" in url:
            url += f"&affid={affiliate_id}"
        else:
            url += f"?affid={affiliate_id}"
    elif "myntra" in url:
        affiliate_id = "your_myntra_affiliate_id"
        if "?" in url:
            url += f"&affid={affiliate_id}"
        else:
            url += f"?affid={affiliate_id}"
    elif "ajio" in url:
        affiliate_id = "your_ajio_affiliate_id"
        if "?" in url:
            url += f"&affid={affiliate_id}"
        else:
            url += f"?affid={affiliate_id}"
    
    return url

# Bot start command
def start(update: Update, context: CallbackContext):
    update.message.reply_text("Welcome! Send me a product link to track its price.")

# Track price command
def track_price(update: Update, context: CallbackContext):
    url = update.message.text.strip()
    new_price = fetch_price(url)
    
    if new_price != "Unsupported URL":
        affiliate_url = convert_to_affiliate_link(url)
        update.message.reply_text(f"Current price: {new_price}. You can buy it here: {affiliate_url}")
        
        # Add product to Firebase
        add_product(update.message.chat_id, affiliate_url, new_price)
    else:
        update.message.reply_text("This product link is not supported. Please send a link from Amazon, Flipkart, Myntra, or Ajio.")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, track_price))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
