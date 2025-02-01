import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
cred = credentials.Certificate("firebase_credentials.json")  # Path to Firebase credentials file
firebase_admin.initialize_app(cred)

# Firebase client
db = firestore.client()

# Add product info to Firebase
def add_product(user_id, url, price):
    doc_ref = db.collection("tracked_products").document(str(user_id))
    doc_ref.set({
        "url": url,
        "initial_price": price,
        "current_price": price
    })

# Get tracked product info
def get_product(user_id):
    doc_ref = db.collection("tracked_products").document(str(user_id))
    doc = doc_ref.get()
    return doc.to_dict() if doc.exists else None

# Update product price in Firebase
def update_price(user_id, price):
    doc_ref = db.collection("tracked_products").document(str(user_id))
    doc_ref.update({
        "current_price": price
    })