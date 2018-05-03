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
    couch = couchdb.Server("http://admin:admin@115.146.86.138:5984")
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
    # infile = sys.argv[1]
    # _id = sys.argv[2]
    count_error = 0
    count_valid = 0
    aurin = {}
    # doc_aurin = {}

    db = connect_to_db("processed_data")

    # with open(infile) as fp:
    infile = 'melbourne_sentiment_iOS_android.json'
    with open(infile) as fp:
        jline = json.load(fp)
        aurin['melbourne'] = jline
        db.save(aurin)
    aurin = {}
    infile = 'victoria_sentiment_iOS_android.json'
    with open(infile) as fp:
        jline = json.load(fp)
        aurin['victoria'] = jline
        db.save(aurin)
    aurin = {}
    infile = 'state_sentiment_iOS_android.json'
    with open(infile) as fp:
        jline = json.load(fp)
        print(jline)
        aurin['state'] = jline
        print(aurin)
        db.save(aurin)
