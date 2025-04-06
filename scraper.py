import requests
from bs4 import BeautifulSoup

# Fallback user agents if fake-useragent fails
DEFAULT_USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'
]

def scrape_price(url):
    try:
        # Try with fake-useragent first
        try:
            from fake_useragent import UserAgent
            ua = UserAgent()
            headers = {'User-Agent': ua.random}
        except:
            # Fallback to rotating default agents
            import random
            headers = {'User-Agent': random.choice(DEFAULT_USER_AGENTS)}
        
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
            
        elif "shopsy" in url:
            price = soup.find("div", class_="_30jeq3")
            return float(price.text.replace("₹", "").replace(",", "")) if price else None
            
    except Exception as e:
        print(f"Scraping error for {url}: {e}")
        return None