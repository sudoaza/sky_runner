# -*- coding: utf-8 -*-
import datetime
import scrapy
import requests
from scrapy.linkextractors import LinkExtractor 
from urllib.parse import urlparse
from newspaper import Article

class NewsSpider(scrapy.Spider):
    name = 'news'

    start_urls = [
        'https://phys.org/search/?search=3d+printing',
        'https://techcrunch.com/tag/3d-printing/',
        'https://www.wired.com/search/?q=3d%20printing&page=1&sort=score',
        'http://discovermagazine.com/search?q=3d+printing',
        'https://www.technologyreview.com/search/?s=3d+printing',
        'https://www.popularmechanics.com/search/?q=3d+printing',
        'https://www.americanscientist.org/search/node/3d%20printing',
        'https://www.fastcompany.com/search?searchkey=3d%20printing',
        'https://www.techradar.com/search?searchTerm=3d+printing',
        'https://3dprinting.com/',
        'https://3dprint.com/',
        'https://3dprintingindustry.com/',
        'https://all3dp.com/',
        'https://www.3dnatives.com/',
        'https://www.3ders.org/',
        'https://www.3dmake.de/'
        ]
    allowed_domains = []
    allowed_domains.extend([urlparse(url).netloc for url in start_urls])

    maxdepth = 2 # max depth for normal pages
    maxsearchdepth = 20 # max depth for search pages or indexes

    def parse(self, response):
        

        if not self.index_page(response) and response.url not in self.start_urls:
            article = Article(response.url)
            article.set_html(response.text)
            article.parse()
            article.nlp()

            item = {}
            item['url'] = response.url
            item['source'] = urlparse(response.url).netloc
            item['title'] = article.title
            if isinstance(article.publish_date, datetime.datetime):
                item['publish_date'] = article.publish_date.isoformat()
            item['keywords'] = ', '.join(article.keywords)
            item['summary'] = article.summary
            item['body'] = article.text
            item['doctype'] = 'article'

            r = requests.post('http://localhost:3000/submit', json={'document': item})

        if response.meta['depth'] >= self.maxdepth and not self.index_page(response):
            return

        if response.meta['depth'] >= self.maxsearchdepth:
            return

        links = LinkExtractor(allow_domains=self.allowed_domains).extract_links(response)
        for link in links:

            url = response.urljoin(link.url)
            print(url)

            # Create a new Request object
            request = response.follow(url, callback=self.parse)

            # Return it thanks to a generator
            yield request
    
    def index_page(self, response):
        url = response.url
        return '/search/' in url or \
            '/tag/' in url or \
            '/page/' in url or \
            'page=' in url or \
            'search=' in url or \
            'query=' in url or \
            'q=' in url or \
            'searchTerm=' in url or \
            '/search?' in url
