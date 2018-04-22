"""
Use Twitter search APIs find tweets from specific location.
Raw tweets are stored in specified couchDB databse.
"""

import logging
import tweepy
import couchdb


class TwitterSearcher():
    """Use Twitter search APIs find tweets from specific location."""

    def __init__(self, api, db, geo, query):
        """Set variables required by Twitter Search API."""
        self.api = api
        self.db = db
        self.geo = geo
        self.query = query

        # API rate call limit.
        self.limit = 100

    def search(self):
        """Search for tweets via Twitter Search API."""
        # Track the upper and lower bound of each returned set.
        lower_id = None
        upper_id = -1

        # Track number of tweets returned in total.
        tweet_count = 0

        # Pull tweets until erorr or no more to process.
        while True:
            try:
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

                # Exit when no new tweets are found.
                if not new_tweets:
                    logging.info("No more tweets to read.")
                    break

                # Process received tweets.
                for tweet in new_tweets:

                    jtweet = tweet._json

                    # Only store tweets that have location we can use.
                    if tweet.coordinates or tweet.place:
                        jtweet['_id'] = str(jtweet['id'])
                        try:
                            self.db.save(jtweet)
                        except couchdb.http.ResourceConflict:
                            logging.info("Ignored duplicate tweet.")

                # Output current number of tweets.
                tweet_count += len(new_tweets)
                logging.info("Downloaded {0} tweets".format(tweet_count))

                # Track upper id.
                upper_id = new_tweets[-1].id

            # Exit upon error.
            except tweepy.TweepError as e:
                logging.error(str(e))
                break