import schedule
import time
from database import get_all_products, update_price
from scraper import scrape_price
from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()

def check_prices():
    bot = Bot(os.getenv("TELEGRAM_TOKEN"))
    products = get_all_products()
    
    for product in products:
        new_price = scrape_price(product['url'])
        if new_price and new_price != product['current_price']:
            update_price(product['_id'], new_price)
            bot.send_message(
                chat_id=product['user_id'],
                text=f"🚨 *Price Alert!*\n\n"
                     f"📦 {product['name']}\n"
                     f"🔽 Old Price: ₹{product['current_price']}\n"
                     f"🔼 New Price: ₹{new_price}\n"
                     f"🔗 [Buy Now]({product['affiliate_link']})",
                parse_mode="Markdown"
            )

schedule.every(1).hours.do(check_prices)

if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(1)