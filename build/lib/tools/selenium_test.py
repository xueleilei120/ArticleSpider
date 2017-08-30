#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: liuyc
@file: selenium.py
@time: 2017/8/25 8:09
@describe:
"""

from selenium import webdriver
from scrapy.selector import Selector



# 通过selenium启动一个chrome浏览器
brower = webdriver.Chrome(executable_path=r"C:\scrapy\resource\chromedriver.exe")
"""
# 抓取淘宝价格
brower.get("https://detail.tmall.com/item.htm?id=16204910274&spm=a223v.7835278.t0.2.63de138KTzGjt&pvid=0b5d6eee-7bfc-49e3-9e0b-3286af182a82&scm=1007.12144.81309.9011_8949&skuId=3607330498269")
t_selctor = Selector(text=brower.page_source)
print(t_selctor.css(".tm-promo-price .tm-price::text").extract())
"""

"""
jobbole登陆
brower.get("http://www.jobbole.com/login/?redirect=http%3A%2F%2Fwww.jobbole.com%2F")
brower.find_element_by_css_selector(".wrapper #jb_user_login ").send_keys("用户名")
brower.find_element_by_css_selector(".wrapper #jb_user_pass ").send_keys("密码")
brower.find_element_by_css_selector("#jb_user_login_btn").click()
"""

# 微博登陆
# brower.get("http://weibo.com/?sudaref=www.baidu.com&retcode=6102")
# 注意：由于微博登陆页面加载时间比较长，会导致提取元素失败，所以需要做延迟
# selenium.common.exceptions.NoSuchElementException: Message: no such element: Unable to locate element: {"method":"css selector","selector":"
# import time
# time.sleep(10)
# brower.find_element_by_css_selector("#loginname").send_keys("loginname")
# brower.find_element_by_css_selector(".info_list.password input[node-type='password']").send_keys("password")
# brower.find_element_by_css_selector(".info_list.login_btn a[node-type='submitBtn']").click()

# # 实现开源中国 滚动下拉
# brower.get("https://www.oschina.net/blog")
# import time
# for i in range(3):
#     brower.execute_script("window.scrollTo(0, document.body.scrollHeight); var lenOfPage=document.body.scrollHeight; return lenOfPage;")
#     time.sleep(5)


# 设置chromedriver不加载图片
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images": 2}
chrome_opt.add_experimental_option("prefs", prefs)
brower = webdriver.Chrome(executable_path=r"C:\scrapy\resource\chromedriver.exe", chrome_options=chrome_opt)
brower.get("https://detail.tmall.com/item.htm?id=16204910274&spm=a223v.7835278.t0.2.63de138KTzGjt&pvid=0b5d6eee-7bfc-49e3-9e0b-3286af182a82&scm=1007.12144.81309.9011_8949&skuId=3607330498269")
brower.quit()

