import os
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def generate_affiliate_link(url):
    parsed = urlparse(url)
    
    if "amazon" in parsed.netloc:
        query = parse_qs(parsed.query)
        query['tag'] = os.getenv("AMAZON_AFFILIATE_ID")
        return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))
    
    elif "flipkart" in parsed.netloc:
        return f"{url}&affid={os.getenv('FLIPKART_AFFILIATE_ID')}"
    
    return url