"""
group 25
* Youshao Xiao - 876548
* Jiaheng Zhu - 1211955
* Lina Zhou - 941539
* Haimei Liu - 895804
* Miaomiao Zhang - 895216

Main script to call either harvester.
Usage: python3 harvester.py <config> <mode> <auth_index>
Where: <config>     -- A json file with configuration information.
       <mode>       -- Mode of usage (stream or search).
       <auth_index> -- Index for authentification information in config.
        nohup python3 crawler.py configure.json stream 0 &
        nohup python3 crawler.py configure.json stream 1 &
        nohup python3 crawler.py configure.json stream 2 &
        nohup python3 crawler.py configure.json stream 3 &
        nohup python3 crawler.py configure.json search 4 &
"""

import sys
import logging
import json
import couchdb
import tweepy
from crawlerStream import TwitterStreamListener
from crawlerSearch import TwitterSearcher

NUM_ARGS = 4
ERROR = 2


def get_database(config):
    """Return handle to couchdb as defined in config file."""
    with open(config) as fp:
        jconfig = json.load(fp)

        try:
            # Pull server information from config.
            server = jconfig['Servers'][0]
            couch = couchdb.Server(server)

            # Check if databse exists, create if not.
            db_name = jconfig['DatabaseName']
            if db_name in couch:
                logging.info("Database {} already exists.".format(db_name))
                db = couch[db_name]
            else:
                logging.info("Created databse {}".format(db_name))
                db = couch.create(db_name)

        except Exception as e:
            logging.error(str(e))
            sys.exit(2)

    return db


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
            logging.error(str(e))
            sys.exit(ERROR)

        return c_key, c_secret, a_token, a_secret


def get_box(config):
    """Return a box representing locations defined in config file."""
    with open(config) as fp:
        jconfig = json.load(fp)

        try:
            box = [
                float(jconfig['Coordinates'][0]),
                float(jconfig['Coordinates'][1]),
                float(jconfig['Coordinates'][2]),
                float(jconfig['Coordinates'][3])
                ]
        except Exception as e:
            logging.error(str(e))
            sys.exit(ERROR)

    return box


def get_geocode(config):
    """Return geocode defined in config file."""
    with open(config) as fp:
        jconfig = json.load(fp)

        try:
            geo = jconfig['Geocode']

        except Exception as e:
            logging.error(str(e))
            sys.exit(ERROR)

    return geo


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s-[line:%(lineno)d]-%(levelname)s: %(message)s')
    if len(sys.argv) != NUM_ARGS:
        logging.error(
            'invalid number of arguments: <harvester.py> <config.json> <mode> '
            '<auth_index>'
            )
        sys.exit(ERROR)

    config = sys.argv[1]
    mode = sys.argv[2]
    auth_index = int(sys.argv[3])

    db = get_database(config)

    c_key, c_secret, a_token, a_secret = get_credentials(config, auth_index)
    auth = tweepy.OAuthHandler(c_key, c_secret)
    auth.set_access_token(a_token, a_secret)
    api = tweepy.API(auth)

    if mode == 'stream':
        box = get_box(config)
        stream_listener = TwitterStreamListener(db)
        stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
        stream.filter(locations=box)
    elif mode == 'search':
        geo = get_geocode(config)
        api = tweepy.API(
            auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True
        )
        searcher = TwitterSearcher(api, db, geo, "*")
        searcher.search()
