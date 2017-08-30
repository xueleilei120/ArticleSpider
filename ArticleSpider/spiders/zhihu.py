# -*- coding: utf-8 -*-
import scrapy
import re
import json


class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/']

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def parse(self, response):
        pass

    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/#signin', headers=self.headers, callback=self.login)]

    def login(self, response):
        post_url = "https://www.zhihu.com/login/phone_num"
        response_text = response.text
        rexsrf_obj = re.match(r'.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)

        xsrf = ""
        if rexsrf_obj:
            xsrf = rexsrf_obj.group(1)

        if xsrf:
            form_data = {
                "_xsrf": xsrf,
                "password": "86816137",
                "captcha_type": "cn",
                "phone_num": "13584870659",
            }

            return [scrapy.FormRequest(url=post_url, headers=self.headers, formdata=form_data, callback=self.check_login)]



    def check_login(self, response):
        dict_text = json.loads(response.text)
        if 'msg' in dict_text and dict_text["msg"] == "登录成功":
            for url in self.start_urls:
                pass





