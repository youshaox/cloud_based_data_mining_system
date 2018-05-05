
from textblob import TextBlob
import json
from shapely.geometry import shape, Point
import pandas as pd
import time
import mel_lga_name as ndata
import couchdb
import sys
import emoji
import logging

STATE_GEO_FILE_NAME = "geojson/australia_state.geojson"
MEL_DIST_GEO_FILE_NAME = "geojson/melbourne_geo.json"
VIC_DIST_GEO_FILE_NAME = "geojson/vic_lga_gov.json"

# def extract_emojis(str):
#   return ''.join(c for c in str if c in emoji.UNICODE_EMOJI)

def average_bounding_box(box):
    """Average list of 4 bounding box coordinates to a midpoint."""
    lng = 0
    lat = 0
    for i in range(len(box[0])):
        lng += box[0][i][0]
        lat += box[0][i][1]
    lat /= 4
    lng /= 4

    return float(lng), float(lat)


# Check Geometry
def isvalid(geom):
    try:
        shape(geom)
        return 1
    except:
        return 0


# split the location of user Melbourne, Victoria
# return the state name
def get_state_by_user_location(location_of_user):
    # if it is in other state
    for item1 in ndata.STATE_NAME:
        if item1 in location_of_user.upper():
            return item1

    # if short name is used
    for item2 in ndata.SHORT_FOR_STATE:
        if item2 in location_of_user.upper():
            return ndata.STATE_NAME[ndata.SHORT_FOR_STATE.index(item2)]

    return None


def get_mel_dist(location_of_user):
    for item in ndata.MEL_DISTRICT_NAME:
        if item in location_of_user.upper():
            return item
    return None


def get_vic_dist(location_of_user):
    for item in ndata.VIC_DISTRICT_NAME:
        if item in location_of_user.upper():
            return item
    return None


# find the name of district within victoria by coordinates
def get_vic_dist_by_coordinate(vic_geo, point):

    name = None
    # district_vic: dict
    for vicdistrict in vic_geo:  # list
        if point.within(shape(vicdistrict['geometry'])):
            name = vicdistrict['properties']['vic_lga__3']
            break
    return name


# find the name of state within Australia by coordinates
def get_state_by_coordinate(state_geo1, point1):
    name = None
    for state_geo0 in state_geo1:  # list
        if point1.within(shape(state_geo0['geometry'])):
            name = state_geo0['properties']['STATE_NAME']
            break
    return name


# find the name of district within melbourne by coordinates
def get_mel_dist_by_coordinate(melb_geo, point):

        name = None
        for district0 in melb_geo:  # list
            if point.within(shape(district0['geometry'])):
                name = district0['properties']['name']
                # print(name)
                break
        file.close()
        return name


# iOS :1, Android -1, none: 0
def get_system(source):
    t = ['iphone', 'iPhone', 'ipad', 'iPad,', 'iOS']
    t2 = ['android', 'Android']
    find = 0
    for iOS in t:
        if iOS in source:
            find = 1
            break
    for android in t2:
        if android in source:
            find = -1
    return find


def tag_tweets(line, mel_geo, vic_geo, state_geo):
    """tag raw tweets with suburb, city in Victoria, State, sentiment score and the kind of mobile
    and end system, store them in processed database"""
    count = 0

    # initialization
    coordinate = None
    score = 0
    state_name = None
    mel_district = None
    vic_district = None
    system = 0
    emoji_list = None

    # use the coordinate of tweet to find the location name
    if line['coordinates2']:
        raw = line['coordinates2']['coordinates']
        coordinate = tuple(raw)
    elif line['coordinates']:
        # get the central point of a place
        raw = average_bounding_box(line['coordinates'])
        coordinate = tuple(raw)

    point = Point(coordinate)
    state_name = get_state_by_coordinate(state_geo, point)
    vic_district = get_vic_dist_by_coordinate(vic_geo, point)
    mel_district = get_mel_dist_by_coordinate(mel_geo, point)

    if line['location']:
        if not state_name:
            state_name = get_state_by_user_location(line['location'])
        if not vic_district:
            vic_district = get_vic_dist(line['location'])
        if not mel_district:
            mel_district = get_mel_dist(line['location'])

    # put all name in upper case
    if state_name:
        state_name = state_name.upper()
    if vic_district:
        vic_district = vic_district.upper()
    if mel_district:
        if mel_district == "Melbourne (3000)" or mel_district == "Melbourne (3004)":
            mel_district = "MELBOURNE"
        mel_district = mel_district.upper()

    # tag and store if location exists
    if state_name or vic_district or mel_district:

        # get sentiment score
        blob = TextBlob(line['text'])
        score = blob.sentiment.polarity

        # get emoji list
        # emoji_list = extract_emojis(line['text'])

        # get the name of mobile end system
        system = get_system(line['source'])

        # count = count + 1
        stored_tweet = {
            'system': system, 'sentiment': score, 'state': state_name, 'districtInMel': mel_district,
            'districtInVic': vic_district }  #, 'emoji_list':emoji_list}
        return stored_tweet

    else:
        logging.info("No location found.")
        return None


# create design document for processed_data DB
def designdoc_processed(couch, mel_geo, vic_geo, state_geo):
    processed_data_db = couch['processed_data']
    db_raw = couch['raw_tweets']
    design_doc = {
        '_id':'_design/try2',
        'views':{
            'viewST': {
                'map':'function(doc){emit(doc.id,{"coordinates":doc.place.bounding_box.coordinates,"coordinates2":doc.coordinates,"location":doc.user.location,"source":doc.source,"text":doc.text});}'
            }
        }
    }

    for line0 in db_raw.view('try/viewST'):
        line = line0['value']
        result = tag_tweets(line, mel_geo, vic_geo, state_geo)

    processed_data_db.save(design_doc)

    results = processed_data_db.view('try2/view1')
    for row in results:
        print(row['value'])

#cteate design document for raw_tweets DB
def designdoc_raw(couch):
    raw_tweets_db = couch['raw_tweets']
    design_doc = {
        '_id':'_design/try2',
        'views':{
            'viewST': {
                'map':'function(doc){emit(doc.id,{"coordinates":doc.place.bounding_box.coordinates,"coordinates2":doc.coordinates,"location":doc.user.location,"source":doc.source,"text":doc.text});}'
            }
        }
    }
    raw_tweets_db.save(design_doc)


#cteate design document for aurin DB
def designdoc_aurin(couch):
    aurin_db = couch['aurin']
    design_doc = {
        '_id':'_design/try2',
        'views':{
            'view1': {
                'map':'function(doc){emit(doc.id,doc);}'
            }
        }
    }

    aurin_db.save(design_doc)


def designdoc_geo(couch):
    geo_db = couch['geo_data']
    design_doc = {
        '_id': '_design/try2',
        'views': {
            'view1': {
                'map': 'function(doc){emit(doc.id,doc);}'
            }
        }
    }

    geo_db.save(design_doc)


def designdoc_pro_data(couch):

    geo_db = couch['geo_data']
    design_doc = {
        '_id': '_design/try3',
        'views': {
            'view1': {
                'map': 'function(doc){emit(doc.id,doc);}'
            }
        }
    }

    geo_db.save(design_doc)


if __name__ == '__main__':
    couch = couchdb.Server('http://admin:admin@115.146.86.138:5984/')

    # read three geo file into memory
    state_geo_info0 = open(STATE_GEO_FILE_NAME, 'r')
    state_geo_info = json.load(state_geo_info0)
    state_geo = state_geo_info['features']

    vic_geo_file = open(VIC_DIST_GEO_FILE_NAME, 'r')
    vic_geo0 = json.load(vic_geo_file)
    vic_geo = vic_geo0['features']

    file = open(MEL_DIST_GEO_FILE_NAME, 'r')
    mel_geo0 = json.load(file)
    mel_geo = mel_geo0['features']

    designdoc_processed(couch, mel_geo, vic_geo, state_geo)
