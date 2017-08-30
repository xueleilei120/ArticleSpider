# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json


import MySQLdb
import MySQLdb.cursors
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi

from ArticleSpider.settings import MYSQL_HOST, MYSQL_DBNAME, MYSQL_USER, MYSQL_PASSWORD


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding="utf-8")


    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)

        return item


    def spider_closed(self, spider):
        self.file.close()

class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value["path"]
                item["front_image_path"] = image_file_path

        return item

class MysqlPipeline(object):
    # 采用同步的机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DBNAME, charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()


    def process_item(self, item, spider):

        insert_sql = """
            insert into scrap_test(title, image, tag)
            VALUES (%s, %s, %s)
        """

        name = item["title"][:10]
        self.cursor.execute(insert_sql, (name, item["front_image_path"], item["tags"]))
        self.conn.commit()


class MysqlTwistedPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常, 添加异常回掉函数
        query.addErrback(self.handle_error, item, spider)

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        #执行具体的插入
        #根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, params = item.get_insert_sql()
        # print(insert_sql, params)
        cursor.execute(insert_sql, params)


class ElasticsearchPipeline(object):
    #将数据写入到es中

    def process_item(self, item, spider):
        #将item转换为es的数据
        item.save_to_es()

        return item