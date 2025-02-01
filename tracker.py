import requests
from bs4 import BeautifulSoup

# Fetch price from Amazon
def fetch_amazon_price(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    try:
        price = soup.find('span', {'id': 'priceblock_ourprice'}).text.strip()
    except AttributeError:
        price = "Price not available"
    
    return price

# Fetch price from Flipkart
def fetch_flipkart_price(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    try:
        price = soup.find('div', {'class': '_30jeq3'}).text.strip()
    except AttributeError:
        price = "Price not available"
    
    return price

# Fetch price from Myntra
def fetch_myntra_price(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    try:
        price = soup.find('span', {'class': 'pdp-price'}).text.strip()
    except AttributeError:
        price = "Price not available"
    
    return price

# Fetch price from Ajio
def fetch_ajio_price(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    try:
        price = soup.find('span', {'class': 'price'}).text.strip()
    except AttributeError:
        price = "Price not available"
    
    return price

# General function to fetch price based on URL
def fetch_price(url):
    if "amazon" in url:
        return fetch_amazon_price(url)
    elif "flipkart" in url:
        return fetch_flipkart_price(url)
    elif "myntra" in url:
        return fetch_myntra_price(url)
    elif "ajio" in url:
        return fetch_ajio_price(url)
    else:
        return "Unsupported URL"