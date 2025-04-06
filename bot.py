import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from database import add_product, get_user_products, stop_tracking
from scraper import scrape_price
from utils import generate_affiliate_link
from dotenv import load_dotenv

load_dotenv()

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "🛒 *Price Tracker Bot*\n\n"
        "Send me product links from:\n"
        "• Amazon\n• Flipkart\n• Ajio\n• Shopsy\n\n"
        "I'll track prices and alert you of changes!",
        parse_mode="Markdown"
    )

def handle_message(update: Update, context: CallbackContext):
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
            
            update.message.reply_text(
                f"✅ *Tracking Started!*\n\n"
                f"💰 *Current Price:* ₹{price}\n"
                f"🔗 [Product Link]({affiliate_link})",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            update.message.reply_text("❌ Couldn't fetch price. Please try again later.")
    else:
        update.message.reply_text("⚠️ Only Amazon/Flipkart/Ajio/Shopsy links are supported")

def list_products(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    products = get_user_products(user_id)
    
    if products:
        message = "📋 *Your Tracked Products:*\n\n"
        for product in products:
            message += f"• [{product['name']}]({product['url']}) - ₹{product['current_price']}\n"
        update.message.reply_text(message, parse_mode="Markdown")
    else:
        update.message.reply_text("You're not tracking any products yet.")

def main():
    updater = Updater(os.getenv("TELEGRAM_TOKEN"))
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("list", list_products))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()