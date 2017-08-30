# -*- coding: utf-8 -*-
from datetime import datetime
import scrapy
from scrapy.http import Request
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from selenium import webdriver
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

from items import LagouJobItemLoader, LagouJobItem
from ArticleSpider.utils.common import get_md5

class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['www.lagou.com', 'www.lagou.com/jobs']
    start_urls = ['https://www.lagou.com/zhaopin/C/']
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
    }
    rules = (
        # Rule(LinkExtractor(allow=("zhaopin/.*",)), callback='parse_job', follow=True),
        # Rule(LinkExtractor(allow=("gongsi/j\d+.html",)), callback='parse_job', follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_job', follow=True),
    )

    ####################### 通过selenium启动一个chrome浏览器 ###########################
    def __init__(self):
        # 通过selenium启动一个chrome浏览器
        # 将webdriver放到spider中可以达到更好的并发效果，也可以在爬虫结束时关闭 Chrome
        self.brower = webdriver.Chrome(executable_path=r"C:\scrapy\resource\chromedriver.exe")
        super(LagouSpider, self).__init__()
        dispatcher.connect(self.close_brower, signals.spider_closed)

    def close_brower(self):
        # 当爬虫退出的时候关闭chrome
        print("---------> spider_closed close_brower <---------")
        self.brower.quit()
     ###################################################################################

    def parse_job(self, response):
        #解析拉勾网的职位
        item_loader = LagouJobItemLoader(item=LagouJobItem(), response=response)
        item_loader.add_css("title", ".job-name::attr(title)")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("salary", ".job_request .salary::text")
        item_loader.add_xpath("job_city", "//*[@class='job_request']/p/span[2]/text()")
        item_loader.add_xpath("work_years", "//*[@class='job_request']/p/span[3]/text()")
        item_loader.add_xpath("degree_need", "//*[@class='job_request']/p/span[4]/text()")
        item_loader.add_xpath("job_type", "//*[@class='job_request']/p/span[5]/text()")

        item_loader.add_css("tags", '.position-label li::text')
        item_loader.add_css("publish_time", ".publish_time::text")
        item_loader.add_css("job_advantage", ".job-advantage p::text")
        item_loader.add_css("job_desc", ".job_bt div")
        item_loader.add_css("job_addr", ".work_addr")
        item_loader.add_css("company_name", "#job_company dt a img::attr(alt)")
        item_loader.add_css("company_url", "#job_company dt a::attr(href)")
        item_loader.add_value("crawl_time", datetime.now())

        job_item = item_loader.load_item()

        return job_item

    # # 模拟登陆
    # def start_requests(self):
    #     login_url = "https://passport.lagou.com/login/login.html?ts=1503735646602&serviceId=lagou&service=https%253A%252F%252Fwww.lagou.com%252F&action=login&signature=1A16F9EB80AEAA28928124277AB9B68E"
    #     return [Request(url=login_url, headers=self.headers, callback=self.login)]
    #
    # def login(self, response):
    #     a=  0
    #     pass
