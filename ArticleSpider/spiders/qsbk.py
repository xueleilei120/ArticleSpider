# -*- coding: utf-8 -*-
from datetime import datetime
from urllib import parse

import scrapy
from scrapy.http.headers import Headers
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from items import QiuShiArticleItemLoder, QiuShiItem


class QsbkSpider(CrawlSpider):
    name = 'qsbk'
    allowed_domains = ['www.qiushibaike.com']
    start_urls = ['https://www.qiushibaike.com/imgrank/']

    rules = (
        Rule(LinkExtractor(allow=r'article/\d+?'), callback='parse_article', follow=True, process_request='add_header'),
    )

    headers = {
        "HOST": "www.qiushibaike.com",
        "Referer": "https://www.qiushibaike.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    def parse_article(self, response):
        item_loader = QiuShiArticleItemLoder(item=QiuShiItem(), response=response)
        item_loader.add_value("url", response.url)
        item_loader.add_xpath("author", "//div[@class='author clearfix']/a[2]/h2/text()")
        item_loader.add_xpath("content", "//div[@class='article block untagged noline mb15']/div[@id='single-next-link']/div[@class='content']/text()")
        image_url_t = response.xpath("//div[@class='article block untagged noline mb15']/div[@id='single-next-link']/div[@class='thumb']/img/@src").extract_first("")
        if image_url_t:
            image_url = parse.urljoin(response.url, image_url_t)
            item_loader.add_value("front_image_url", [image_url])
        else:
            return

        item_loader.add_value("crawl_time", datetime.now())
        load_item = item_loader.load_item()
        return load_item

    def add_header(self, request):
        request.headers = Headers(self.headers or {})
        return request

    def start_requests(self):
        return [scrapy.Request('https://www.qiushibaike.com', headers=self.headers)]
