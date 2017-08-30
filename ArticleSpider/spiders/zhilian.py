# -*- coding: utf-8 -*-
import scrapy
from datetime import datetime
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


from items import ZhiLianJobItem, ZhiLianJobItemLoader
# from utils.common import get_md5

import hashlib

def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


class ZhilianSpider(CrawlSpider):
    name = 'zhilian'
    allowed_domains = ['sou.zhaopin.com', 'jobs.zhaopin.com']
    start_urls = ['http://sou.zhaopin.com/jobs/searchresult.ashx?jl=%E8%8B%8F%E5%B7%9E&kw=python&sm=0&p=1']

    rules = (
        Rule(LinkExtractor(allow=r'http://jobs.zhaopin.com/\d+.htm'), callback='parse_item', follow=True),
    )

    custom_settings = {
        "DOWNLOAD_DELAY": 3,
    }

    def parse_item(self, response):
        item_loader = ZhiLianJobItemLoader(item=ZhiLianJobItem(), response=response)
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("title", ".top-fixed-box h1::text")
        item_loader.add_xpath("salary", "//div[@class='terminalpage-left']/ul/li[1]/strong/text()")
        item_loader.add_xpath("work_years", "//div[@class='terminalpage-left']/ul/li[5]/strong/text()")
        item_loader.add_xpath("work_city", "//div[@class='terminalpage-left']/ul/li[2]/strong/a/text()")
        item_loader.add_xpath("degree_need", "//div[@class='terminalpage-left']/ul/li[6]/strong/text()")
        item_loader.add_xpath("job_type", "//div[@class='terminalpage-left']/ul/li[8]/strong/a/text()")
        item_loader.add_xpath("publish_time", "//div[@class='terminalpage-left']/ul/li[3]/strong/span/text()")
        item_loader.add_css("job_advantage", ".welfare-tab-box span::text")
        item_loader.add_css("job_desc", ".tab-cont-box div")
        item_loader.add_css("job_addr", ".tab-cont-box .tab-inner-cont h2::text")
        item_loader.add_css("company_url", ".company-name-t a::attr(href)")
        item_loader.add_css("company_name", ".company-name-t a::text")
        item_loader.add_value("crawl_time", datetime.now())
        item_loader.add_xpath("user_nums", "//div[@class='terminalpage-left']/ul/li[7]/strong/text()")
        load_item = item_loader.load_item()

        return load_item
