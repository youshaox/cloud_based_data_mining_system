"""
Use Twitter search APIs find tweets from specific location.
Raw tweets are stored in specified couchDB databse.
This twitter searcher prevents the duplicate dataset return by the API server by using the upper bound and lower bound parameter.
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
        self.limit = 100

    def search(self):
        """Search for tweets via Twitter Search API.
        Since id of each tweet is decreasing in every return dataset and the created time is also decreasing. The first line of the
        return dataset will be the newest created twitter while the last line will be the oldest one in this return dataset.
        """
        # default no lower bound.
        lower_id = None
        # default no upper bounc.
        upper_id = -1

        # Track number of tweets returned in total.
        tweet_count = 0
        count = 0

        # Pull tweets until error or no more to process.
        while True:
            try:
                # if there is no upper bounder
                if (upper_id <= 0):
                    # if there is no lower bound
                    if (not lower_id):
                        new_tweets = self.api.search(
                            q=self.query,
                            geocode=self.geo,
                            count=self.limit
                        )
                    # if there is lower bound
                    else:
                        new_tweets = self.api.search(
                            q=self.query,
                            geocode=self.geo,
                            count=self.limit,
                            since_id=lower_id
                        )
                else:
                    # if there is no lower bound
                    if (not lower_id):
                        new_tweets = self.api.search(
                            q=self.query,
                            geocode=self.geo,
                            count=self.limit,
                            max_id=str(upper_id - 1)
                        )
                    # if there is lower bounder.
                    else:
                        new_tweets = self.api.search(
                            q=self.query,
                            geocode=self.geo,
                            count=self.limit,
                            max_id=str(upper_id - 1),
                            since_id=lower_id
                        )

                # Exit when no new tweets are found.
                if not new_tweets:
                    logging.info("No more tweets to read.")
                    break

                # Process received tweets.
                for tweet in new_tweets:
                    jtweet = tweet._json
                    if tweet.coordinates or tweet.place:
                        # store tweets with geo code.
                        jtweet['_id'] = jtweet['id_str']
                        try:
                            self.db.save(jtweet)
                        except couchdb.http.ResourceConflict:
                            logging.info("Ignored duplicate tweet.")

                # Output current number of tweets.
                tweet_count += len(new_tweets)
                logging.info("Downloaded {0} tweets".format(tweet_count))

                # Track upper id. Use the id of last tweet in the previous return result as the new upper_id.
                upper_id = new_tweets[-1].id
            # Exit upon error.
            except tweepy.TweepError as e:
                logging.error(str(e))
                break