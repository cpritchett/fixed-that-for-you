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
    'apple.com': {
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
