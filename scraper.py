import requests
from bs4 import BeautifulSoup

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
            
        elif "ajio" in url:
            price = soup.find("span", class_="prod-sp")
            return float(price.text.replace("₹", "").replace(",", "")) if price else None
            
    except Exception as e:
        print(f"Scraping error: {e}")
        return None