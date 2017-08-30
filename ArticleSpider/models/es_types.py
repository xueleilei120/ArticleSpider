#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: liuyc
@file: es_types.py
@time: 2017/7/14 17:13
@describe:
"""

from datetime import datetime
from elasticsearch_dsl import DocType, Date, Nested, Boolean, \
    analyzer, InnerObjectWrapper, Completion, Keyword, Text, Integer

from elasticsearch_dsl.analysis import CustomAnalyzer as _CustomAnalyzer

from elasticsearch_dsl.connections import connections
connections.create_connection(hosts=["localhost"])

class CustomAnalyzer(_CustomAnalyzer):
    def get_analysis_definition(self):
        return {}

ik_analyzer = CustomAnalyzer("ik_max_word", filter=["lowercase"])


class ArticleType(DocType):
    # 伯乐在线文章类型
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    front_image_url = Keyword()
    front_image_path = Keyword()
    praise_nums = Integer()
    comment_nums = Integer()
    fav_nums = Integer()
    tags = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")

    class Meta:
        # db_name
        index = "jobbole"
        # table_name
        doc_type = "article"


class ZhiLianJobType(DocType):
    """
    智联职位类型 用于初始化es
    """
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    url = Keyword()
    content = Text(analyzer="ik_max_word")

    class Meta:
        # db_name
        index = "zhilian"
        # table_name
        doc_type = "job"



if __name__ == "__main__":
    ZhiLianJobType.init()
