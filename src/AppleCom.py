import tldextract
from urllib.parse import urlparse


def replace_custom(url):
    '''Apple custom link handler for both Apple News and Apple Stocks'''
    parsed_url = urlparse(url)
    extracted_url = tldextract.extract(url)
    
    # Handle Apple News URLs (apple.news domain)
    if extracted_url.registered_domain == 'apple.news':
        return handle_apple_news(url)
    
    # Handle Apple Stocks URLs (stocks.apple.com subdomain)
    elif extracted_url.registered_domain == 'apple.com' and extracted_url.subdomain == 'stocks':
        return handle_apple_stocks(url)
    
    # Return None for other apple.com URLs we don't handle
    return None


def handle_apple_news(url):
    '''Apple News embedded link extractor'''
    from bs4 import BeautifulSoup
    from urllib.request import Request, urlopen
    
    html_request = Request(url, headers={'User-Agent': 'Mozilla'})
    html_response = urlopen(html_request).read()

    html_soup = BeautifulSoup(html_response, 'html.parser')

    embedded_article_url = html_soup.find_all('span', class_="click-here")[0].parent.get('href')

    return f'https://archive.today/newest/{embedded_article_url}'


def handle_apple_stocks(url):
    '''Apple Stocks link replacement with Yahoo Finance'''
    # Parse the URL to extract stock symbol
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip('/').split('/')
    
    # Handle different Apple Stocks URL formats:
    # https://stocks.apple.com/SYMBOL
    # https://stocks.apple.com/stocks/SYMBOL
    # https://stocks.apple.com/symbol/SYMBOL
    
    symbol = None
    if len(path_parts) == 1 and path_parts[0]:
        # Format: /SYMBOL
        symbol = path_parts[0]
    elif len(path_parts) >= 2 and path_parts[1]:
        # Format: /stocks/SYMBOL or /symbol/SYMBOL
        symbol = path_parts[1]
    
    if symbol:
        # Return Yahoo Finance URL as a more accessible alternative
        return f'https://finance.yahoo.com/quote/{symbol}'
    
    # If we can't parse the symbol, return the archive.today version
    return f'https://archive.today/newest/{url}'