#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 20/4/18
#Import the necessary methods from tweepy library
import couchdb
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json

#Variables that contains the user credentials to access Twitter API
access_token = "879998896352641024-ICJRUTFvj1ob72f6v6bSOv20jkYa8l4"
access_token_secret = "oia0c3TvQylAb9r6Y6CjkypPi9fJ8TobAiR9zUwBP1XVy"
consumer_key = "ajaUmkuRsyLsT8DiAUirS0Sml"
consumer_secret = "jS68ANvd3UYpSQEnHlXZJpRyPxI3QGpaAyirtIQDwszLhVp2ag"


hostname = "localhost"
user = "admin"
password = "admin"
couchserver = couchdb.Server("http://%s:%s@%s:5984/" % (user, password, hostname))


def save_to_couchdb(document, dbname):
    """
    :param document:
    :param dbname:
    :return:
    """

    if dbname in couchserver:
        db = couchserver[dbname]
    else:
        db = couchserver.create(dbname)
    db.save(document)

class StdOutListener(StreamListener):

    def on_data(self, data):
        # save data to couchdb
        document = json.loads(data)
        print(document)
        save_to_couchdb(document, 'test_1')
        print(document)
        # save_to_couchdb(document, 'test')
        return True

    def on_error(self, status):
        print(status)


if __name__ == '__main__':

    #This handles Twitter authetification and the connection to Twitter Streaming API
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)

    #This line filter Twitter Streams to capture data by the keywords: 'python', 'javascript', 'ruby'
    # longitude and latitude pairs
    # stream.filter(track=['Austrlia'])
    stream.filter(locations=[113.6594, -43.00311, 153.61194, -12.46113])