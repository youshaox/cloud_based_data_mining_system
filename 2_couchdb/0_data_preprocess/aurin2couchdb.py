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
    infile = sys.argv[1]
    _id = sys.argv[2]
    count_error = 0
    count_valid = 0
    aurin = {}
    doc_aurin = {}

    db = connect_to_db("aurin")

    with open(infile) as fp:
        jline = json.load(fp)
        infile_name = infile.split(".")[0]
        aurin[infile_name] = jline
        aurin['_id'] = _id
        db.save(aurin)