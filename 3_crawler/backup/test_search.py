#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 24/4/18
"""
function:

"""
import sys
import logging
import json
import couchdb
import tweepy

config="./configure.json"
auth_index=4
ERROR='2'

def get_geocode(config):
    """Return geocode defined in config file."""
    with open(config) as fp:
        jconfig = json.load(fp)

        try:
            geo = jconfig['Geocode']

        except Exception as e:
            # logging.error(str(e))
            print(str(e))
            sys.exit(ERROR)

    return geo

def get_credentials(config, auth_index):
    """Read and return credentials from config file."""
    with open(config) as fp:
        jconfig = json.load(fp)

        # Attempt to read authentification details from config file.
        try:
            c_key = jconfig['Authentication'][auth_index]['consumer_key']
            c_secret = jconfig['Authentication'][auth_index]['consumer_secret']
            a_token = jconfig['Authentication'][auth_index]['access_token']
            a_secret = (
                jconfig['Authentication'][auth_index]['access_secret']
                )

        except Exception as e:
            # logging.error(str(e))
            print(str(e))
            sys.exit(ERROR)

        return c_key, c_secret, a_token, a_secret


class TwitterSearcher():
    """Use Twitter search APIs find tweets from specific location."""

    def __init__(self, api, geo, query):
        """Set variables required by Twitter Search API."""
        self.api = api
        # self.db = db
        self.geo = geo
        self.query = query

        # API rate call limit.
        self.limit = 100

    def search(self):
        print('start')
        lower_id = None
        upper_id = -1
        if (upper_id <= 0):
            if (not lower_id):
                new_tweets = self.api.search(
                    q=self.query,
                    geocode=self.geo,
                    count=self.limit
                )

            else:
                new_tweets = self.api.search(
                    q=self.query,
                    geocode=self.geo,
                    count=self.limit,
                    since_id=lower_id
                )
        else:
            if (not lower_id):
                new_tweets = self.api.search(
                    q=self.query,
                    geocode=self.geo,
                    count=self.limit,
                    upper_id=str(upper_id - 1)
                )
            else:
                new_tweets = self.api.search(
                    q=self.query,
                    geocode=self.geo,
                    count=self.limit,
                    upper_id=str(upper_id - 1),
                    since_id=lower_id
                )
        # print(new_tweets)
        upper_id = new_tweets[-1].id
        for tweet in new_tweets:
            print(tweet.id)
            print(tweet._json)


if __name__ == "__main__":
    c_key, c_secret, a_token, a_secret = get_credentials(config, auth_index)
    auth = tweepy.OAuthHandler(c_key, c_secret)
    auth.set_access_token(a_token, a_secret)
    api = tweepy.API(auth)

    print(c_key)

    geo = get_geocode(config)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    searcher = TwitterSearcher(api, geo, "Chinese")
    searcher.search()
