#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 5/5/18
"""
function:

"""
import sys

#解决 二进制str 转 unicode问题
# reload(sys)
# sys.setdefaultencoding('utf8')



# json = [{"1":{"name":"couchdb"}}, {"2":{"name":"couchdb2"}}]
# for js in json:
#     print(js['couchdb'])
inventory_list = [{"s_type":"combo", "s_num":2, "ip_list":['115.146.86.214']}]

print(inventory_list[0]["ip_list"])
# for json in jsons:
#     print(json)