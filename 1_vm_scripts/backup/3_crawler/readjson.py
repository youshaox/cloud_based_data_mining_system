#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 27/4/18
"""
function:

"""
import json

infile = "search6.json"
# outfile = "test.json"

if __name__ == '__main__':
    with open(infile, 'r') as df:
        lines = df.readlines()
        print(len(lines))
        for line in lines:
            jline = json.loads(line)
            # print(jline)
            # print(type(jline))
            # print(jline['user'])


