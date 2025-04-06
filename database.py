from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client["PriceTrackerDB"]
products = db["products"]

def add_product(user_id, url, price, affiliate_link):
    products.update_one(
        {"user_id": user_id, "url": url},
        {"$set": {
            "current_price": price,
            "affiliate_link": affiliate_link,
            "last_checked": datetime.now()
        }},
        upsert=True
    )

def get_user_products(user_id):
    return list(products.find({"user_id": user_id}))