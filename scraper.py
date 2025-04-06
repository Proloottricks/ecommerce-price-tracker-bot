import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

ua = UserAgent()

def scrape_price(url):
    headers = {'User-Agent': ua.random}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if "amazon" in url:
            price = soup.find("span", class_="a-price-whole")
            return float(price.text.replace(",", "")) if price else None
            
        elif "flipkart" in url:
            price = soup.find("div", class_="_30jeq3")
            return float(price.text.replace("₹", "").replace(",", "")) if price else None
            
        # Add similar logic for Ajio/Shopsy
        
    except Exception as e:
        print(f"Scraping error: {e}")
        return None