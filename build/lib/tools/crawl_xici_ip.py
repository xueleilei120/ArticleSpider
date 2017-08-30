#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: liuyc
@file: crawl_xici_ip.py
@time: 2017/8/21 23:22
@describe:
"""
import requests
from scrapy.selector import Selector
from fake_useragent import UserAgent
import MySQLdb


conn = MySQLdb.connect(host="127.0.0.1", user="root", password="pass", db="scrapy", charset="utf8")
cursor = conn.cursor()
ua = UserAgent()


def crawl_xici_ips():
    headers = {"User-Agent": "{0}".format(ua.random)}
    for i in range(1, 3):
        req = requests.get("http://www.xicidaili.com/nn/{0}".format(i), headers=headers)
        selector = Selector(text=req.text)
        trs = selector.css("#ip_list tr")

        lst_ip = []
        for tr in trs[1:]:
            all_text = tr.css("td::text").extract()
            lst_ip.append({"ip": all_text[0], 'port': all_text[1], 'ip_type': all_text[5]})

        for ip_info in lst_ip:
            sql_insert = "INSERT INTO ip_proxy(ip, port, ip_type) VALUES ('{0}','{1}','{2}')".format(
                    ip_info["ip"], ip_info["port"], ip_info["ip_type"])
            cursor.execute(sql_insert)
            conn.commit()


# crawl_xici_ips()


class GetIP(object):

    def get_random_ip(self):
        random_sql = "SELECT ip, port FROM ip_proxy ORDER BY RAND() LIMIT 1"
        cursor.execute(random_sql)
        for ip_info in cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            judge_re = self.judge_ip(ip, port)
            if judge_re:
                return "http://{0}:{1}".format(ip, port)
            else:
                return self.get_random_ip()

    def del_ip(self, ip):
        # 从数据库中删除无效ip
        del_sql = "DELETE FROM ip_proxy WHERE ip='{0}'".format(ip)
        try:
            cursor.execute(del_sql)
            conn.commit()
        except Exception as e:
            print(e)

    def judge_ip(self, ip, port):
        baidu_rul = "http://www.baidu.com"
        proxy_url = "http://{0}:{1}".format(ip, port)
        proxy_dict = {
            "http": proxy_url,
        }
        try:
            response = requests.get(baidu_rul, proxies=proxy_dict)
        except Exception as e:
            print(e)
            self.del_ip(ip)
            print("invalid ip or port")
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print("effective ip:{0}".format(ip))
                return True
            else:
                print("invalid ip or port")
                self.del_ip(ip)
                return False
#
# if __name__ == "__main__":
#     get_ip_obj = GetIP()
#     get_ip_obj.get_random_ip()