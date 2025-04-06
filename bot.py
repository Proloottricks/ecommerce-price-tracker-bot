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
from database import add_product, get_user_products, stop_tracking
from scraper import scrape_price
from utils import generate_affiliate_link
from dotenv import load_dotenv

load_dotenv()

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
    # Builder pattern without inline comments
    application = (
        Application.builder()
        .token(os.getenv("TELEGRAM_TOKEN"))
        .read_timeout(60)
        .get_updates_read_timeout(60)
        .pool_timeout(60)
        .build()
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    try:
        print("Starting bot...")
        application.run_polling(
            poll_interval=3.0,
            timeout=60,
            drop_pending_updates=True,
            close_loop=False
        )
    except Exception as e:
        print(f"Bot error: {e}")
    finally:
        print("Bot stopped")

if __name__ == "__main__":
    main()