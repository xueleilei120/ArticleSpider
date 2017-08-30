# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent


from tools.crawl_xici_ip import GetIP


class ArticlespiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgentMiddleware(object):
    """
    随机获取更换用户代理 agent
    """
    def __init__(self, crawler):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua_type = crawler.settings.get("AGETN_TYPE", "random")
        self.ua = UserAgent()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        s = "RandomUserAgentMiddleware"
        print(s.center(20, "*"))
        def get_ua():
            ua = getattr(self.ua, self.ua_type) # 此用法非常的巧妙 --> self.ua.random = self.ua.self.ua_type
            return ua
        # 设置headers中的User-Agent
        request.headers.setdefault("User-Agent", get_ua())


class RandomProxyMiddleware(object):
    """
    随机免费代理ip中间件
    """
    def process_request(self, request, spider):
        s = "RandomProxyMiddleware"
        print(s.center(20, "*"))
        get_ip_obj = GetIP()
        request.meta["proxy"] = get_ip_obj.get_random_ip()

from scrapy.http import HtmlResponse


class JsPageMiddleware(object):
    """
    selenium模拟浏览器抓取js动态网页 中间件
    每次spider request的时候都会进入这里
    """
    def process_request(self, request, spider):
        if spider.name == "jobbole":
            # 注意： url=request.url
            spider.brower.get(url=request.url)
            import time
            time.sleep(3)
            print("访问：url={0}".format(request.url))
            # 返回response downloder就不会再去执行 避免重发处理 注意： url=spider.brower.current_url
            return HtmlResponse(request=request, url=spider.brower.current_url, encoding="utf-8", body=spider.brower.page_source)

