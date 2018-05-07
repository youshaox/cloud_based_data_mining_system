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
    couch = couchdb.Server("http://admin:admin@115.146.86.21:5984")
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
                try:
                    save_to_couchdb(db, jtweet)
                    count_valid += 1
                    logging.info("We have saved" + str(count_valid))
                except couchdb.http.ResourceConflict:
                    logging.info("Duplicated tweet! Discard")
                    continue
            except json.decoder.JSONDecodeError:
                logging.info("can't resolve this line! Discard")
                count_error += 1
                continue
    logging.info("Finish!")
