# aggregate_sentiment_analysis

This is the current version of data processing procedures, which uses MapReduce functions are used to access and conduct *_sum* and *_count* calculation on tagged tweets to get the final statistical result, which will be accessed by web server through Views. With *crontab*, the reduce function can be called every minute.

Sentiment analysis consists of five files:

1. file /mapfunctions contains the map functions used to create views .
2. create_View.py is used to create views in couchdb to access data.
3. mel_lga_name.py is the name of different areas in Australia.
4. aggregrate_result.py is used to calculate the result.
5. Realtime.sh is used to do aggregrate in real time.



## 1. Prerequisites

```
pip install couchdb
```

## 2. Introduction

### 2.1 map_functions

The files contains the .js file of map function to create views, district.js, emoji_Mel.js, emoji_State.js, emoji_Vic.js, get_doc.js, process_raw.js, sentiment.js, system.js.

### 2.2 create_View.py

The *create_View()* function create a view in CouchDB and returns a dictionary with the properties of the view. 

### 2.3 mel_lga_name.py

The name of different areas in Australia, state names, name of districts in Victoria, name of suburbs in Melbourne

###2.4 aggregrate_result.py

The aim of this module is to create final result for web server. The number of valid tweets, the average sentiment score, the proportion of iOS and Android system and the most frequently used emoji in each state of Australia, in each distract of Victoria, are in each suburb of Melbourne are needed to conduct this social media data analysis. 

This module uses the MapReduce function to access and aggregate the processed tweets in CouchDB by creating Views. 

### 2.5 realtime.sh

Using this funciton, the result_data will be runned every one minute

