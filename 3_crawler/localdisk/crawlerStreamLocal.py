"""Class to listen to twitter stream using Streaming API."""
import logging
import json
from tweepy.streaming import StreamListener


class TwitterStreamListener(StreamListener):
    """Listen using Twitter Streaming API."""

    def __init__(self, filename):
        """Store reference to couchdb."""
        self.filename = filename

    def on_data(self, data):
        """Store tweet"""
        jtweet = json.loads(data)
        jtweet['_id'] = str(jtweet['id'])
        with open(self.filename, 'a') as tf:
            print(json.dumps(jtweet), file=tf)
        return True

    def on_error(self, status_code):
        """Log error message."""
        logging.error(status_code)