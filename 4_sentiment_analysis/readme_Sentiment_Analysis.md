# Sentiment Analysis

This is the old version of data processing procedures, which uses python to conducts data pre-processing and final data analysis. The sentiment analyzer should first obtain the raw data in CouchDB by View, then conducts analysis and at last stores the processed data back into CouchDB, in the database *tagged_tweet*. Another python module named analysis_result will then access the tagged data and do final calculation to get the analysis result required by web server and front-end web application.  

Sentiment analysis consists of five files:

1. file /geojson contains the geographical information.
2. create_design.py is used to create views in couchdb to access data.
3. process_data.py is used to process raw tweets and store in new storage.
4. Analysis_result.py is used to calculate the result

```
# use python3 to run program
python3 process_data.py
python3 analysis_result.py
```

## 1. Prerequisites

```
#install python3.6
sudo apt-get update
sudo apt-get install python3.6

#install python textbolb
sudo apt install python3.6-pip
pip install -U pip
pip install --upgrade pip
sudo pip install -U textblob
sudo python3.6 -m textblob.download_corpora

# install python Shapely
sudo pip install Shapely

# install couchdb
sudo pip install couchdb

# install pandas
pip install pandas

# insall emoji
pip install emoji
```

## 2. Introduction

### 2.1 geojson

This file contains the geographical files of Australia, Victoria, Melbourne are used, which are in /geojson, australia_state.geojson, vic_lga_gov.json, and melbourne_geo.json, are obtained from data.gov.au. 

### 2.2 create_design.py

This module uses the library couchdb to create views to access data ,for example, _design/try/viewST is used to access the raw tweet data.

### 2.3 process_data.py

This module processes raw tweets and stores processed data in new storage, which has the hugest amount of calculation to decide the location name of tweets. 

### 2.4 analysis_result.py

This moduloe is used to calculate the sentiment result and the mobile system result in states, victoria and melbourne, thereby creating final result for web server.

### Chanlleges:

1. Time-consuming calcualtion in getting location name
2. duplicate creating views to database, which may return conflict error



