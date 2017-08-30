# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
import datetime
import re
import redis
from w3lib.html import remove_tags



from ArticleSpider.settings import SQL_DATETIME_FORMAT
from ArticleSpider.models.es_types import ArticleType, ZhiLianJobType

from elasticsearch_dsl.connections import connections
es = connections.create_connection(ArticleType._doc_type.using)
redis_client = redis.StrictRedis()

class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ArticleItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


def return_value(value):
    return value


def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums


def remove_comment_tags(value):
    # 去掉tag中提取的评论
    if "评论" in value:
        return ""
    else:
        return value


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()

    return str(create_date)

def gen_suggests_ex(index, tuple_info):
    userd_words = set()
    suggests = []
    for text, weight in tuple_info:
        if text:
            analyze_text = es.indices.analyze(index=index, analyzer="ik_max_word", body=text, params={"filter": ["lowercase"]})
            analyze_words = set([r["token"] for r in analyze_text["tokens"] if len(r["token"]) > 1])
            new_words = analyze_words - userd_words
            userd_words = new_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input": list(new_words), "weight":weight})

    return suggests


class JobBoleArticleItem(scrapy.Item):
    title = scrapy.Field()
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert),
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")
    )
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into jobbole(title, url, fav_nums )
            VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE fav_nums=VALUES(fav_nums)
        """
        params = (self["title"], self["url"], self["fav_nums"])

        return insert_sql, params

    def save_to_es(self):
        article = ArticleType()
        article.title = self['title']
        article.create_date = self["create_date"]
        article.content = remove_tags(self["content"])
        article.front_image_url = self["front_image_url"]
        if "front_image_path" in self:
            article.front_image_path = self["front_image_path"]
        article.praise_nums = self["praise_nums"]
        article.fav_nums = self["fav_nums"]
        article.comment_nums = self["comment_nums"]
        article.url = self["url"]
        article.tags = self["tags"]
        article.meta.id = self["url_object_id"]

        article.suggest = gen_suggests_ex(ArticleType._doc_type.index, ((article.title, 10), (article.tags, 7)))
        article.save()
        # 累计伯乐文章
        redis_client.incr("jobbole_count")
        return



def replace_splash(value):
    return value.replace("/", "")


def handle_strip(value):
    return value.strip()


def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    return "".join(addr_list)


class LagouJobItemLoader(ItemLoader):
    # 自定义itemloader
    default_output_processor = TakeFirst()


class LagouJobItem(scrapy.Item):
    # 拉钩网职位信息
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(replace_splash),
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(replace_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(replace_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(
        input_processor=MapCompose(handle_strip),
    )
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, handle_jobaddr),
    )
    company_name = scrapy.Field(
        input_processor=MapCompose(handle_strip),
    )
    tags = scrapy.Field(
        input_processor=Join(",")
    )
    company_url = scrapy.Field()
    crawl_time = scrapy.Field()


    def get_insert_sql(self):
        insert_sql = """insert INTO lagoujob(url, url_object_id, title, salary, job_city, work_years,
                          degree_need, job_type, publish_time, job_advantage, job_desc, job_addr,
                          company_url, company_name, crawl_time)
                          VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE job_desc=VALUES(job_desc)
                """

        params = (self["url"], self["url_object_id"], self["title"], self["salary"], self["job_city"],
                  self["work_years"], self["degree_need"], self["job_type"], self["publish_time"],
                  self["job_advantage"], self["job_desc"], self["job_addr"], self["company_url"],
                  self["company_name"], self["crawl_time"].strftime(SQL_DATETIME_FORMAT),)
        return insert_sql, params


def get_salary_min(value):
    match_re = re.match(r"(\d+)-", value)
    if match_re:
        num = int(match_re.group(1))
    else:
        match_re_t = re.match(r"(\d+)", value)
        if match_re_t:
            num =int(match_re_t.group(1))
        else:
            num = 0
    return num


def get_salary_max(value):
    match_re = re.match(r".*-(\d+)", value)
    if match_re:
        num = int(match_re.group(1))
    else:
        match_re_t = re.match(r"(\d+)", value)
        if match_re_t:
            num = int(match_re_t.group(1))
        else:
            num = 0
    return num

def handle_job_addr(value):
    addrs = value.split("\r\n")
    addrs = [item.strip() for item in addrs]
    return ''.join(addrs)


class ZhiLianJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


class ZhiLianJobItem(scrapy.Item):
    # 拉钩网职位信息
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    title = scrapy.Field()
    salary = scrapy.Field()
    work_years = scrapy.Field()
    work_city = scrapy.Field()
    degree_need = scrapy.Field()
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(handle_job_addr)
    )
    company_url = scrapy.Field()
    company_name = scrapy.Field()
    crawl_time = scrapy.Field()
    user_nums = scrapy.Field(
            input_processor=MapCompose(get_nums)
    )

    def get_insert_sql(self):
        insert_sql = """INSERT INTO zhilian(url, url_object_id, title, salary_min, salary_max,
            work_years, work_city, degree_need, publish_time, job_advantage,
            job_desc, job_addr, company_url, company_name, crawl_time, user_nums, job_type) VALUES (%s,
            %s, %s,%s, %s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s, %s) ON DUPLICATE KEY
            UPDATE job_desc=VALUES(job_desc), salary_max=VALUES(salary_max), job_type=VALUES(job_type) """

        salary_min = get_salary_min(self["salary"])
        salary_max = get_salary_max(self["salary"])
        url_t = self.get("url", "")
        url_object_id_t = self.get("url_object_id", "")
        title_t = self.get("title", "")
        work_years_t = self.get("work_years", "")
        job_advantage_t = self.get("job_advantage", "")
        work_city_t = self.get("work_city", "")
        degree_need_t = self.get("degree_need", "")
        publish_time_t = self.get("publish_time", "")
        job_desc_t = self.get("job_desc", "")
        job_addr_t = self.get("job_addr", "")
        company_url_t = self.get("company_url", "")
        company_name_t = self.get("company_name", "")
        user_nums_t = self.get("user_nums", 0)
        job_type_t = self.get("job_type", "")
        params = (url_t, url_object_id_t, title_t, salary_min, salary_max,
                  work_years_t, work_city_t, degree_need_t, publish_time_t,
                  job_advantage_t, job_desc_t, job_addr_t, company_url_t,
                  company_name_t, self["crawl_time"], user_nums_t, job_type_t
                  )
        return insert_sql, params

    def save_to_es(self):
        job = ZhiLianJobType()
        job.title = self.get("title", "")
        job.url = self.get("url", "")
        job.content = self.get("desc", "")
        job.meta.id = self.get("url_object_id", "")
        job.suggest = gen_suggests_ex(ZhiLianJobType._doc_type.index, ((job.title, 10),))
        job.save()

        redis_client.incr("zhilian_job_count")
        return


# 糗事百科
class QiuShiArticleItemLoder(ItemLoader):
    default_output_processor = TakeFirst()

import django
django.setup()
from scrapy_djangoitem import DjangoItem
from qsbk.models import QiuShiArticle

class QiuShiItemEx(DjangoItem):
    django_model = QiuShiArticle

class QiuShiItem(scrapy.Item):
    url = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor=MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    crawl_time = scrapy.Field()

    def save_to_django(self):
        obj = QiuShiItemEx()
        if "author" in self:
            obj["author"] = self["author"]
        obj["url"] = self["url"]
        obj["content"] = self["content"]
        if "front_image_path" in self:
            obj["image"] = self["front_image_path"]
        obj["crawl_time"] = self["crawl_time"]
        obj.save()
        return







