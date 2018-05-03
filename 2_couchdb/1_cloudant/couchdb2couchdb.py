#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 29/4/18
"""
function:
nohup python text2couchdb.py stream0.json &
"""
import sys
import couchdb
import json
import logging


def connect_to_db(db_name, ip):
    couch = couchdb.Server("http://admin:admin@{}:5984".format(ip))
    if db_name in couch:
        logging.info("Database {} already exists.".format(db_name))
        db = couch[db_name]
    else:
        logging.info("Created databse {}".format(db_name))
        db = couch.create(db_name)
    return db

def save_to_couchdb(db, jtweet):
    db.save(jtweet)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s-[line:%(lineno)d]-%(levelname)s: %(message)s')
    from_db = connect_to_db("tweets_source","115.146.95.74")
    # to_db = connect_to_db("tweets_source")
    count=0
    for document in from_db:
        count+=1
        if count>=10:
            break
        print(document)