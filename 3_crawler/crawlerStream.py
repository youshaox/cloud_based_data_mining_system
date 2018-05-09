"""Class to listen to twitter stream using Streaming API."""
import logging
import json
import couchdb
from tweepy.streaming import StreamListener
import tag_tweet

class TwitterStreamListener(StreamListener):
    """Listen using Twitter Streaming API."""

    def __init__(self, db):
        """Store reference to couchdb."""
        self.db = db

    def on_data(self, data):
        """Store tweet, if not already seen."""
        jtweet = json.loads(data)

        # get tagged tweet as njtweet
        njtweet = tag_tweet.tag_tweets(jtweet)

        # store valid tagged tweet
        if njtweet is not None:
            njtweet['_id'] = jtweet['id_str']
            try:
                # print(njtweet)
                self.db.save(njtweet)
            except couchdb.http.ResourceConflict:
                logging.info("Ignored duplicate tweet.")

    def on_error(self, status_code):
        """Log error message."""
        logging.error(status_code)

