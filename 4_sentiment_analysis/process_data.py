"""
group 25
* Youshao Xiao - 876548
* Jiaheng Zhu - 848432
* Lina Zhou - 941539
* Haimei Liu - 895804
* Miaomiao Zhang - 895216

process raw tweets and store in new storage:
processed tweets structure:
Sentiment:(float)
system:(string)android/iOS
state: (string)'NEW SOUTH WALES', 'VICTORIA', 'QUEENSLAND', 'SOUTH AUSTRALIA',
         'TASMANIA', 'WESTERN AUSTRALIA', 'AUSTRALIA CAPITAL TERRITORY', 'NORTHERN TERRITORY'
DistrictInMel: district in Melboune
DistrictInVic: district in victoria
emoji_list: [] list of the emojis in the tweet

"""
from collections import Counter
from textblob import TextBlob
import json
from shapely.geometry import shape, Point
import time
import mel_lga_name as ndata
import create_design as cdview
import couchdb
import sys
import emoji
import logging
#from TextParser import *
import emoji_unicode_ranking as eur
import create_View

start = time.clock()

PROCESSED_DB_NAME = "processed_data_new_system"
DB_RAW_NAME = 'raw_tweets'
server_instance = couchdb.Server('http://admin:admin@115.146.86.138:5984/')

STATE_GEO_FILE_NAME = "geojson/australia_state.geojson"
MEL_DIST_GEO_FILE_NAME = "geojson/melbourne_geo.json"
VIC_DIST_GEO_FILE_NAME = "geojson/vic_lga_gov.json"


def extract_emojis(str):
    """extract the emojis used in tweet using python emoji package"""
    return ''.join(c for c in str if c in emoji.UNICODE_EMOJI)

def get_most_used_eomji(str):
    if str:
        return Counter(str).most_common()[0][0]
    else:
        return None

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

def get_state_by_user_location(location_of_user):
    """split the location of user Melbourne, Victoria , return the state name"""

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



def get_vic_dist_by_coordinate(vic_geo, point):
    """
    :param vic_geo: the geojson file of victoria
    :param point: tweet's coordinate
    :return: the district name in victoria
    """
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



def get_system(source):
    """
    :param source: source of a tweet
    :return: the system type of the user ,iOS :1, Android -1, none: 0
    """
    t = ['iphone', 'iPhone', 'ipad', 'iPad,', 'iOS']
    t2 = ['android', 'Android']
    find = None
    for iOS in t:
        if iOS in source:
            find = "IOS"
            break
    for android in t2:
        if android in source:
            find = "AND"
    return find


def tag_tweets(view, db_pro, mel_geo, vic_geo, state_geo):
    """tag raw tweets with suburb, city in Victoria, State, sentiment score and the kind of mobile
    and end system, store them in processed database"""
    count = 0

    for line0 in view:
        if count > 300:
            break
        line = line0['value']
        # check whether the tweet has been processed
        if 'processed' in line0:
            if line0['processed1']:
                continue

        # get tweet id
        id = line0['id']

        # initialization of coordinate
        coordinate = None

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

            # TextParser.getStopWords()
            # textParser = TextParser()

            # get sentiment score
            blob = TextBlob(line['text'])
            #blob = TextBlob(textParser.parsing(line['text']))
            score = blob.sentiment.polarity

            # get emoji list
            emoji_list = extract_emojis(line['text'])

            if score == 0:
                if len(emoji_list) > 0:
                    rank = 0
                    for e in emoji_list:
                        # print(e)
                        # print(eur.EMOJI_UNICODE_RANKING.keys())
                        if e in eur.EMOJI_UNICODE_RANKING.keys():
                            rank += eur.EMOJI_UNICODE_RANKING[e]

                    score = rank / len(emoji_list)

            # get the name of mobile end system
            system = get_system(line['source'])
            to_store_emoji = get_most_used_eomji(emoji_list)

            stored_tweet = {
                'system': system, 'sentiment': score, 'state': state_name, 'districtInMel': mel_district,
                'districtInVic': vic_district, 'emoji_list':to_store_emoji}

            db_pro.save(stored_tweet)
            count += 1
            doc = db_raw.get(id)
            doc['processed1'] = True
            db_raw.save(doc)

        else:
            continue

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
    # couch = couchdb.Server(DB_RAW_ADDRESS)
    try:
        db_raw = server_instance[DB_RAW_NAME]
    except Exception:
        logging.error("Raw tweets DB does not exist.")
        sys.exit(2)

    # create view to raw_tweets database
    #cdview.designdoc_raw(couch)

    create_View.create_view(server_instance, DB_RAW_NAME, "process_raw", None)
    view = create_View.get_view(server_instance, DB_RAW_NAME, "process_raw/process_raw", None)

    # create processed tweets db.
    if PROCESSED_DB_NAME in server_instance:
        db_pro = server_instance[PROCESSED_DB_NAME]
        print("already has the db")
    else:
        db_pro = server_instance.create(PROCESSED_DB_NAME)
        print('create new processed database')

    tag_tweets(view, db_pro, mel_geo, vic_geo, state_geo)

    state_geo_info0.close()
    vic_geo_file.close()
    file.close()

    end = time.clock()
    print('Running time: %s Seconds' % (end - start))


