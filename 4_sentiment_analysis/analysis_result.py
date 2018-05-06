"""
# calculate the sentiment result and the mobile system result in states, victoria and melbourne
# write result in json file
# {"area name": [average sentiment score, iOS system percentage, android system percentage}
# create 3 result file:
# state_sentiment_iOS_android.json
# victoria_sentiment_iOS_android.json
# melbourne_sentiment_iOS_android.json

"""
import lga_name as ndata
import couchdb
import logging
import sys
import create_design as cdview

PROCESSED_DB_NAME = "processed_data2"
RESULT_DB_NAME = "result_data_emoji2"


def get_result(area_result):
    """calculate average sentiment score, system usage proportion.
    {"area":[average sentiment score, iOS percentage, Android percentage}"""

    for area, result1 in area_result.items():
        if result1[3] > 0:
            tmp = area_result[area][0] / area_result[area][3]
            area_result[area][0] = tmp
        if (result1[1] + result1[2]) > 0:
            tmp2 = result1[1] / (result1[1] + result1[2])
            area_result[area][1] = tmp2
            area_result[area][2] = 1 - tmp2

        list0 = area_result[area][4]
        if list0:
            area_result[area][4] = max(list0, key=lambda x: list0[x])

    return area_result


def sum_up_tag_tweet(db_pro, mel_result, vic_result, state_result):
    """read processed tweets, sum up area result"""
    # initialization
    for key0 in state_result.keys():
        state_result[key0] = [0.0, 0.0, 0.0, 0,{}]
    for key1 in mel_result.keys():
        mel_result[key1] = [0.0, 0.0, 0.0, 0,{}]
    for key2 in vic_result.keys():
        vic_result[key2] = [0.0, 0.0, 0.0, 0,{}]

    # read processed twitter
    for tweet0 in db_pro.view('try/viewPD2'):
        tweet = tweet0['value']
        state_name = tweet['state']
        mel_district_name = tweet['districtInMel']
        vic_district_name = tweet['districtInVic']

        emoji_dict = {}
        emoji0 = tweet['emoji_list']
        if emoji0:
            for e in emoji0:
                if e in emoji_dict.keys():
                    emoji_dict[e] += 1
                else:
                    emoji_dict[e] = 1

        if state_name:
            state_result[state_name][0] += tweet['sentiment']
            state_result[state_name][3] += 1
            if tweet['system'] == 1:
                state_result[state_name][1] += 1
            if tweet['system'] == -1:
                state_result[state_name][2] += 1
            if emoji_dict:
                state_result[state_name][4] = emoji_dict

        if vic_district_name :
            vic_result[vic_district_name][0] += tweet['sentiment']
            vic_result[vic_district_name][3] += 1
            if tweet['system'] == 1:
                vic_result[vic_district_name][1] += 1
            if tweet['system'] == -1:
                vic_result[vic_district_name][2] += 1
            if emoji_dict:
                vic_result[vic_district_name][4] = emoji_dict
        if mel_district_name:
            mel_result[mel_district_name][0] += tweet['sentiment']
            mel_result[mel_district_name][3] += 1
            if tweet['system'] == 1:
                mel_result[mel_district_name][1] += 1
            if tweet['system'] == -1:
                mel_result[mel_district_name][2] += 1
            if emoji_dict:
                mel_result[mel_district_name][4] = emoji_dict

    return mel_result, vic_result, state_result


if __name__ == "__main__":
    state_population = dict.fromkeys(ndata.STATE_NAME, 0)
    melbourne_population = dict.fromkeys(ndata.MEL_DISTRICT_NAME, 0)
    victoria_population = dict.fromkeys(ndata.VIC_DISTRICT_NAME, 0)

    state_result = dict.fromkeys(ndata.STATE_NAME)
    vic_result = dict.fromkeys(ndata.VIC_DISTRICT_NAME)
    mel_result = dict.fromkeys(ndata.MEL_DISTRICT_NAME)

    couch = couchdb.Server('http://admin:admin@115.146.86.21:5984/')
    try:
        db_pro = couch[PROCESSED_DB_NAME]
    except Exception:
        logging.error("processed tweets DB does not exist.")
        sys.exit(2)

    # create view to access processed data
    cdview.designdoc_pro_data(couch)

    tmp = sum_up_tag_tweet(db_pro, mel_result, vic_result, state_result)
    # get average sentiment score and system usage proportion

    if RESULT_DB_NAME in couch:
        result_db = couch[RESULT_DB_NAME]
    else:
        result_db = couch.create(RESULT_DB_NAME)

    result_db.save(get_result(tmp[2]))
    result_db.save(get_result(tmp[1]))
    result_db.save(get_result(tmp[0]))
