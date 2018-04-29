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

def connect_to_db(db_name):
    couch = couchdb.Server("http://admin:admin@127.0.0.1:5984")
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
    logging.basicConfig(level=logging.INFO)
    infile = sys.argv[1]
    count_error = 0
    count_valid = 0

    db = connect_to_db("raw_tweets")

    with open(infile, 'r', encoding='utf-8') as df:
        line = df.readline()
        while line:
            line = df.readline()
            try:
                jtweet = json.loads(line)
                count_valid += 1
                save_to_couchdb(db, jtweet)
            except json.decoder.JSONDecodeError:
                count_error += 1
                continue
    logging.info("Finish!")
