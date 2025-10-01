import tldextract

class LinkParser():
  __valid_domains = {
     #'bsky.app': {
     #  'type': 'social',
     #  'replacement': 'bskyx.app'
     #},
    'instagram.com': {
      'type': 'social',
      'replacement': 'ddinstagram.com'
    },
    'bloomberg.com': {
      'type': 'news'
    },
    'nytimes.com': {
      'type': 'news'
    },
    'apple.news': {
      'type': 'custom'
    },
    'theatlantic.com': {
      'type': 'news'
    },
    # 'threads.net': {
    #   'type': 'social',
    #   'replacement': 'vxthreads.net'
    # },
    'tiktok.com': {
      'type': 'social',
      'replacement': 'vxtiktok.com'
    },
    'twitter.com': {
      'type': 'social',
      'replacement': 'vxtwitter.com'
    },
    'washingtonpost.com': {
      'type': 'news'
    },
    'wsj.com': {
      'type': 'news'
    },
    'x.com': {
      'type': 'social',
      'replacement': 'vxtwitter.com'
    },
    'expressnews.com': {
      'type': 'news'
    },
    'newsweek.com': {
      'type': 'news'
    },
    'forbes.com': {
      'type': 'news'
    },
    'haaretz.com': {
      'type': 'news'
    },
    'latimes.com': {
      'type': 'news'
    },
    'houstonchronicle.com': {
      'type': 'news'
    },
    'stltoday.com': {
      'type': 'news'
    }
  }
  
  def __init__(self, url) -> None:
    self.url = url
    self.extracted_url = tldextract.extract(url)

  def fix(self):
    # Special case: Handle Apple Stocks URLs (stocks.apple.com)
    if (self.extracted_url.registered_domain == 'apple.com' and 
        self.extracted_url.subdomain == 'stocks'):
      return self.handle_apple_stocks()
    
    # Check if it's a valid domain
    try:
      domainInfo = self.__valid_domains[self.extracted_url.registered_domain]
    except Exception:
      return None

    # Execute the relevant replacement function and return
    if domainInfo['type'] == 'social':
      return self.replace_social(domainInfo)
    elif domainInfo['type'] == 'news':
      if 'unlocked_article_code' in self.url:
        return None
      else:
        return self.replace_news()
    elif domainInfo['type'] == 'custom':
      '''Load module based on domain name of source in TitleCase'''
      from re import sub

      module_name = sub(r"(\.)+", " ", self.extracted_url.registered_domain).title().replace(" ", "").replace("*","")
      custom_module = getattr(__import__('src', fromlist=[module_name]), module_name)

      return custom_module.replace_custom(url=self.url)

    return None

  def replace_social(self, domainInfo: object):
    '''Social media link replacement'''
    fqdn = self.extracted_url.fqdn
    new_url = self.url.replace(fqdn, domainInfo['replacement'])
    return new_url

  def replace_news(self):
    '''News link replacement'''
    new_url = f'https://archive.today/newest/{self.url}'
    return new_url

  def handle_apple_stocks(self):
    '''Apple Stocks link replacement with Yahoo Finance'''
    from urllib.parse import urlparse
    
    # Parse the URL to extract stock symbol
    parsed_url = urlparse(self.url)
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
    return f'https://archive.today/newest/{self.url}'
