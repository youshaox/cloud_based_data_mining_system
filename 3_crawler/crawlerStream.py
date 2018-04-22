"""Class to listen to twitter stream using Streaming API."""
import logging
import json
import couchdb
from tweepy.streaming import StreamListener


class TwitterStreamListener(StreamListener):
    """Listen using Twitter Streaming API."""

    def __init__(self, db):
        """Store reference to couchdb."""
        self.db = db

    # def clean_twitter(self, jtweet):
    #     """
    #     extract only part of the data
    #     :param jtweet:
    #     :return:
    #     """
    #     nid = str(jtweet["id"])
    #     ntext = jtweet['text']
    #     ncoordinates = jtweet['coordinates']
    #     nuser = jtweet['user']
    #     ntime = jtweet['created_at']
    #     nplace = jtweet['place']
    #     nentities = jtweet['entities']
    #     nsource = jtweet['source']
    #
    #     jtweet = {'_id': nid, 'text': ntext, 'user': nuser,
    #             'coordinates': ncoordinates, 'create_time': ntime,
    #             'place': nplace, 'entities': nentities, 'source': nsource,
    #             'addressed': False}
    #     return jtweet

    def on_data(self, data):
        """Store tweet, if not already seen."""
        jtweet = json.loads(data)
        jtweet['_id'] = str(jtweet['id'])
        # jtweet = self.clean_twitter(jtweet)
        try:
            self.db.save(jtweet)
        except couchdb.http.ResourceConflict:
            logging.info("Ignored duplicate tweet.")

    def on_error(self, status_code):
        """Log error message."""
        logging.error(status_code)