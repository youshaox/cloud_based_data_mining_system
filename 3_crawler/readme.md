# Twitter Harvester

Twitter Harvester consists of four files: 

1. configure.json is responsible for the configuragtion info.
2. crawler.py is used to call the crawlerSearch.py (search API) and crawlerStream.py (Streaming API)
3. crawlerSearch.py
4. crawlerStream.py

```shell
# use the streaming api with the authoriation key 0
python3 crawler.py configure.json stream 0

# use the search api with the authoriation key 1
python3 crawler.py configure.json search 1
```

## 1. Prerequisites

```
sudo apt-get install python3
pip3 install couchdb
pip3 install tweepy
```

## 2. Introduction

###  2.1 configure.json

This file specifies:

1. the configuration keys for the crawlers. 
2. The couchdb server address.
3. coordinates used in the streaming API
4. geocode used in the search API
5. database name

### 2.2 crawler.py

check the arguments and call the corresponding crawler.

### 2.3 crawlerStream.py 

Harverst tweets from the streaming API and save the tweets in the couchdb.

**Avoid the duplicate tweets**

1. id/id_str is the unique id of each tweet. So id_str is used as the "\_id" in the couchdb where "_id" is also unqiue in the couchdb. So a duplicate tweet will cause resource conflicts when it is saved to the couchdb. We use this method to avoid the duplicate tweets in our project.


2. Also id_str(string) should be used rather than id (number) due to some programming languages may have difficulty/silent defects in interpreting it.

https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/tweet-object

### 2.4 crawlerSearch.py

Harverst tweets from the search API and save the tweets in the couchdb.

#### 2.4.1 Avoid the duplicate tweets in the same way

#### 2.4.2 Get the tweets most effectively

REST APIs of tweet search is stateless. That means you could get a lot of duplicate tweets in each request. But there is rate limit for each account. This in turn wastes the resource. So we use pagination by specifying the max_id and since_id to get our tweets very effectively.

Also you could sepcifiy the upper bound and lower bound to get the tweets in the required time interval .

https://www.karambelkar.info/2015/01/how-to-use-twitters-search-rest-api-most-effectively./

## Chanlleges:

1. duplicate tweets:

   Bloomfilter is firstly used to avoid the duplicate tweets. But the usage of the native property of couchdb  (unique _id)makes this process more convenient and effective.

2. proxy handler

   At first, proxy handler is thought to be used to handle with the anti-crawler techniques. That is to say crawlling the proxy websites and use available proxy IPs for our crawler. However the usage of the twitter API makes this process simple. Also the rate limit is imposed on each account.

## TEST

With the prerequisites installed and authoriation key provided in configure.json file and couchdb installed in the local system, our system could be tested using the following commands:

```shell
# use the streaming api with the authoriation key 0
python3 crawler.py configure.json stream 0

# use the search api with the authoriation key 1
python3 crawler.py configure.json search 1
```
