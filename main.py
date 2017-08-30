#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: liuyc
@file: main.py
@time: 2017/3/29 23:01
@describe:
"""

from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "jobbole"])
# execute(["scrapy", "crawl", "lagou"])
# execute(["scrapy", "crawl", "zhihu"])
# execute(["scrapy", "crawl", "zhilian"])
execute(["scrapy", "crawl", "qsbk"])


