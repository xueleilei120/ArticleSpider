#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: liuyc
@file: common.py
@time: 2017/4/3 16:30
@describe:
"""

# -*- coding: utf-8 -*-
__author__ = 'bobby'
import hashlib
import re


def get_md5(url):
    if isinstance(url, str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()