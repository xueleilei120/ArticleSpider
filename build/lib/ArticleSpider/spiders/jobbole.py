# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from urllib import parse
from selenium import webdriver

from ArticleSpider.items import JobBoleArticleItem, ArticleItemLoader
from ArticleSpider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = "jobbole"
    allowed_domains = ["python.jobbole.com"]
    start_urls = ['http://python.jobbole.com/all-posts/aaaaaaa']

    # 自定义设置
    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        # "JOBDIR": "job_info/001",
    }

    # def __init__(self):
    #     # 通过selenium启动一个chrome浏览器
    #     # 将webdriver放到spider中可以达到更好的并发效果，也可以在爬虫结束时关闭 Chrome
    #     self.brower = webdriver.Chrome(executable_path=r"C:\scrapy\resource\chromedriver.exe")
    #     super(JobboleSpider, self).__init__()
    #     dispatcher.connect(self.close_brower, signals.spider_closed)
    #
    # def close_brower(self):
    #     # 当爬虫退出的时候关闭chrome
    #     print("spider_closed close_brower")
    #     self.brower.quit()
    # 设置可以处理404页面
    # 收集伯乐在线所有404的url以及404页面数
    handle_httpstatus_list = [404]

    # 注意： **kwargs一定要加
    def __init__(self, **kwargs):
        self.fail_urls = []
        # 信号使用
        dispatcher.connect(self.handle_spider_close, signals.spider_closed)

    def handle_spider_close(self):
        self.crawler.stats.set_value("failed_urls", ','.join(self.fail_urls))

    def parse(self, response):
        """
        1. 获取文章列表页中的文章url并交给scrapy下载后并进行解析
        2. 获取下一页的url并交给scrapy进行下载， 下载完成后交给parse
        """

        if response.status == 404:
            self.fail_urls.append(response.url)
            # 数据收集器 存在于self.crawler
            self.crawler.stats.inc_value("fail_url_num")
            # scrapy好多扩展都是通过信号进行的

        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        num = 0
        for post_node in post_nodes:
            num += 1
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            # parse.urljoin(response.url, post_url) -> 避免有的url为 当前路径+网址路径
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url}, callback=self.parse_detail)
            if num > 10:
                break

    def parse_detail(self, response):
        front_image_url = response.meta.get("front_image_url", "")
        item_loader = ArticleItemLoader(item=JobBoleArticleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "a[href='#article-comment'] span::text")
        item_loader.add_css("content", "div.entry")

        article_item = item_loader.load_item()
        yield article_item

