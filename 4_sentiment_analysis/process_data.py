# #####################################################
# process raw tweets and store in new storage:
# tweets structure:
# Sentiment:(float)
# system:(string)android/iOS
# state: (string)'NEW SOUTH WALES', 'VICTORIA', 'QUEENSLAND', 'SOUTH AUSTRALIA',
#          'TASMANIA', 'WESTERN AUSTRALIA', 'AUSTRALIA CAPITAL TERRITORY', 'NORTHERN TERRITORY'
# Melbourne:(Int) 1/0
# Victoria: (Int) 1/0
# DistrictInMel: district in melboune
# DistrictInVic: district in victoria
#
#
# #####################################################
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

start = time.clock()

PROCESSED_DB_NAME = "processed_data2"
DB_RAW_ADDRESS = 'http://admin:admin@115.146.86.21:5984/'
DB_RAW_NAME = 'raw_tweets'

STATE_GEO_FILE_NAME = "geojson/australia_state.geojson"
MEL_DIST_GEO_FILE_NAME = "geojson/melbourne_geo.json"
VIC_DIST_GEO_FILE_NAME = "geojson/vic_lga_gov.json"


def extract_emojis(str):
  return ''.join(c for c in str if c in emoji.UNICODE_EMOJI)

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


def tag_tweets(db_raw, db_pro, mel_geo, vic_geo, state_geo):
    """tag raw tweets with suburb, city in Victoria, State, sentiment score and the kind of mobile
    and end system, store them in processed database"""
    count = 0

    for line0 in db_raw.view('try/viewST'):
        line = line0['value']

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
            emoji_list = extract_emojis(line['text'])

            # get the name of mobile end system
            system = get_system(line['source'])

            # count = count + 1
            stored_tweet = {
                'system': system, 'sentiment': score, 'state': state_name, 'districtInMel': mel_district,
                'districtInVic': vic_district, 'emoji_list':emoji_list}
            db_pro.save(stored_tweet)

        else:
            logging.info("No location found.")

    return None


if __name__ == "__main__":

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

    # Get raw tweets db.
    couch_raw = couchdb.Server(DB_RAW_ADDRESS)
    try:
        db_raw = couch_raw[DB_RAW_NAME]
    except Exception:
        logging.error("Raw tweets DB does not exist.")
        sys.exit(2)

    # Get processed tweets db.
    couch_pro = couchdb.Server(DB_RAW_ADDRESS)
    if PROCESSED_DB_NAME in couch_pro:
        db_pro = couch_pro[PROCESSED_DB_NAME]
        print("already has the db")
    else:
        db_pro = couch_pro.create(PROCESSED_DB_NAME)
        print('here')

    tag_tweets(db_raw, db_pro, mel_geo, vic_geo, state_geo)

    state_geo_info0.close()
    vic_geo_file.close()
    file.close()

    end = time.clock()
    print('Running time: %s Seconds' % (end - start))
