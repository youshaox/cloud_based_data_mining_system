import tweepy
import time
import json
from couchdb import Server


server = Server('http://admin:admin@127.0.0.1:5984/')

try:
    db_tweets = server['tweets_source']
except:
    db_tweets = server.create('tweets_source')

# Variables that contains the user credentials to access Twitter API (lina)
consumer_key = "jFgpCP4G99xyRMlB3mvSoNToB"
consumer_secret = "GGKrP8Xo8a4yLMwN5o94NvpyMFIQfDdDYxIGRHFo5pnmVRnthN"
access_token = "987903261196734465-bm06Nhe1ryit2F3lJA3pS0tvdJQWZeX"
access_token_secret = "dwmaKwY2vTUmiayrRXN4o8kdeHxd4dFASEcMiQuG8ehzJ"

# Variables that contains the user credentials to access Twitter API (lina)
consumer_key = "DydHyhqn7ATRGqqrlTHW4Scxx"
consumer_secret = "orhq5C4UDNYBSn4LlvSfivZJ1qekb1mR7bAB5PtdBxMmvJoFXi"
access_token = "987903311595520000-5d1Ys7LFxmV6J3cFEF5hdTicu3TFroR"
access_token_secret = "d603J716wneTf3EqFCdtUILRqL5HEpOOOTvFRFug9paj0"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

# AU. Source: http://boundingbox.klokantech.com/
GEOBOX_AU=[113.6594, -43.00311, 153.61194, -12.46113]

# Put your search term
# searchquery = "*"

contents = tweepy.Cursor(api.search, q="Chinese",
                         geocode="-37.9726,145.0531,66km", lang="en").items()

count = 0
errorCount = 0


while True:
    try:
        content = next(contents)
        print(content)
        count += 1
        # use count-break during dev to avoid twitter restrictions
        # if (count>10):
        #    break
    except tweepy.TweepError:
        # catches TweepError when rate limiting occurs, sleeps, then restarts.
        # nominally 15 minutes, make a bit longer to avoid attention.
        print("sleeping....")
        time.sleep(60 * 16)
        content = next(contents)
    except StopIteration:
        break
    try:
        print("Writing to JSON tweet number:" + str(count))
        # json.dump(content._json,file,sort_keys = True,indent = 4)

        njson = json.dumps(content._json, ensure_ascii=False)
        doc = json.loads(njson)
        print(doc)
        nid = doc['id_str']
        print(doc)
        if nid in db_tweets:
            print('--------already have----------------')

        else:
            ntext = doc['text']
            ncoordinates = doc['coordinates']
            nuser = doc['user']
            ntime = doc['created_at']
            nplace = doc['place']
            nentities = doc['entities']
            nsource = doc['source']
            ndoc = {'_id': nid, 'text': ntext, 'user': nuser,
                    'coordinates': ncoordinates, 'create_time': ntime,
                    'place': nplace, 'entities': nentities, 'source':nsource,
                    'addressed': False}
            db_tweets.save(ndoc)
            print(nid)
            print('-------------------------------------')

    except UnicodeEncodeError:
        errorCount += 1
        print("UnicodeEncodeError,errorCount =" + str(errorCount))