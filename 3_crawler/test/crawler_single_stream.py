# source: https://github.com/KaiqiYang94/comp90024-australiacityanalytics/blob/master/tweetsreader/TweetsStreamDownload.py
import couchdb
import json
import queue
import sys
import time
import tweepy
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.streaming import StreamListener
from couchdb import Server

GEOBOX_AU=[113.6594, -43.00311, 153.61194, -12.46113]

accounts = [] # for fetching status
dbNameSource = 'source'
dbNameResult = 'result'
coudb_ip='127.0.0.1'

# claire
consumer_key = "pLUeC3mnT9Gc4fWTn1TGGeKEy"
consumer_secret = "0vpMFXQbeX8KJExPNcXdC29XSMhSNFPwySgOezSDk3tyDTumnS"
access_token = "987483594338717697-3REZtI0Hng44beI3RZldE0w4dAOfaQ0"
access_token_secret = "aL5mcxS9Sef2lwRX1mLflDiVKywBbsltOF0tpDlDSQBD5"


# account setting
# lina
accounts.append({
'consumer_key' : 'jFgpCP4G99xyRMlB3mvSoNToB',
'consumer_secret' : 'GGKrP8Xo8a4yLMwN5o94NvpyMFIQfDdDYxIGRHFo5pnmVRnthN',
'access_token' : '987903261196734465-bm06Nhe1ryit2F3lJA3pS0tvdJQWZeX',
'access_secret' : 'dwmaKwY2vTUmiayrRXN4o8kdeHxd4dFASEcMiQuG8ehzJ'})

# shawn
# accounts.append({
# 'consumer_key' : 'ajaUmkuRsyLsT8DiAUirS0Sml',
# 'consumer_secret' : 'jS68ANvd3UYpSQEnHlXZJpRyPxI3QGpaAyirtIQDwszLhVp2ag',
# 'access_token' : '879998896352641024-ICJRUTFvj1ob72f6v6bSOv20jkYa8l4',
# 'access_secret' : 'oia0c3TvQylAb9r6Y6CjkypPi9fJ8TobAiR9zUwBP1XVy'})

# mia
accounts.append({
'consumer_key' : 'MP8YNprO1W7taLeRCa5NNpfxu',
'consumer_secret' : 'm4f5ciNz7LjUhTXzjJECx4YFnjdqoOtHoB7jY41IK9aAnjsTke',
'access_token' : '973516180869672960lFSKG5YPbPWC0UEzDsAwNsc',
'access_secret' : '4my1VFndjuPmfi22nZNUI2K62G8Bb5edH6f5rMNIn6pfe'})

# gavin
accounts.append({
'consumer_key' : 'DydHyhqn7ATRGqqrlTHW4Scxx',
'consumer_secret' : 'orhq5C4UDNYBSn4LlvSfivZJ1qekb1mR7bAB5PtdBxMmvJoFXi',
'access_token' : '987903311595520000-5d1Ys7LFxmV6J3cFEF5hdTicu3TFroR',
'access_secret' : 'd603J716wneTf3EqFCdtUILRqL5HEpOOOTvFRFug9paj0'})

# claire
accounts.append({
'consumer_key' : 'pLUeC3mnT9Gc4fWTn1TGGeKEy',
'consumer_secret' : '0vpMFXQbeX8KJExPNcXdC29XSMhSNFPwySgOezSDk3tyDTumnS',
'access_token' : '987483594338717697-3REZtI0Hng44beI3RZldE0w4dAOfaQ0',
'access_secret' : 'aL5mcxS9Sef2lwRX1mLflDiVKywBbsltOF0tpDlDSQBD5'})

# add accounts to apis
apis = []
for account in accounts:
    auth = OAuthHandler(account['consumer_key'], account['consumer_secret'])
    auth.set_access_token(account['access_token'], account['access_secret'])
    apis.append(tweepy.API(auth))
print("Accounts added")



couchdbIP = 'http://admin:admin@' + coudb_ip + ':5984/'  # IP of master couchdb
couchserver = couchdb.Server(couchdbIP)
try:
    db = couchserver['tweets']
except:
    db = couchserver.create('tweets')


class ReaderListener(StreamListener):

    def on_data(self, data):
        try:

            doc = json.loads(data)
            nid = doc["id_str"]

            if nid in db:
                print('--------alread have--------')
                return True
            else:
                # tweets
                ntext = doc['text']
                # geo cooridinates
                ncoordinates = doc['coordinates']
                nuser = doc['user']
                ntime = doc['created_at']
                nplace = doc['place']
                nentities = doc['entities']
                # phone type
                nsource = doc['source']

                ndoc = {'_id': nid, 'text': ntext, 'user': nuser,
                        'coordinates': ncoordinates, 'create_time': ntime,
                        'place': nplace, 'entities': nentities, 'source':nsource,
                        'addressed': False}

                # save_to_couchdb(ndoc, 'test1')
                db.save(ndoc)
                print(ndoc)
                return True
        except BaseException as e:
            print("Error on_data: %s" % str(e))
        return True

    def on_error(self, status_code):
        print(status_code)
        return True

if __name__ == '__main__':
    # This handles Twitter authetification and the connection to Twitter
    # Streaming API
    listener = ReaderListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, listener)

    # This line filter Twitter Streams to capture data by the keywords: '.',
    # almost all tweets
    stream.filter(locations=GEOBOX_AU, languages=["en"])