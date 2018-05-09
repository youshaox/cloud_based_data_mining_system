"""
group 25
* Youshao Xiao - 876548
* Jiaheng Zhu - 848432
* Lina Zhou - 941539
* Haimei Liu - 895804
* Miaomiao Zhang - 895216
"""
import couchdb
import create_View
import mel_lga_name as ndata
import time
start = time.clock()

PROCESSED_DB_NAME = "tagged_tweet"
RESULT_DB_NAME = "final_result"



def save_result(result_db0, group_level, server):
    """
    :param result_db: the name of result database
    :param group_level:
            group_level = 1 for the number of tweets on each state
            group_level = 2 for the number of tweets on each district in Victoria
            group_level = 3 for the number of tweets on each district in Melbourne
    :param server: the name of server instance
    :return: saving result to database
            result:dict{ average sentiment score, iOS percentage, android percentage, population, most used emoji, biggest emoiji used frequency}
    """
    if group_level == 1:
        index = 0
        result = dict.fromkeys(ndata.STATE_NAME)
    if group_level == 2:
        index = 1
        result = dict.fromkeys(ndata.VIC_DISTRICT_NAME)
    if group_level == 3:
        index = 2
        result = dict.fromkeys(ndata.MEL_DISTRICT_NAME)

    # initialization of result dict
    for key0 in result.keys():
        result[key0] = [0.0, 0.0, 0.0, 0, None, 0]

    # get population
    create_View.create_view(server, PROCESSED_DB_NAME, "district", "_count")
    view_population = create_View.get_view(server, PROCESSED_DB_NAME, "district/district", g_level=group_level)
    for row in view_population:
        if row.key[index]:
            result[row.key[index]][3] = row.value

    # get average sentiment score
    create_View.create_view(server, PROCESSED_DB_NAME, "sentiment", "_sum")
    view_sentiment = create_View.get_view(server, PROCESSED_DB_NAME, "sentiment/sentiment", g_level=group_level)
    for row1 in view_sentiment:
        if row1.key[index]:
            result[row1.key[index]][0] = row1.value / result[row1.key[index]][3] # to get average sentiment score

    if group_level == 1:
        # group_level = 2 for the number of each system on each state
        create_View.create_view(server, PROCESSED_DB_NAME, "system", "_count")
        view_system = create_View.get_view(server, PROCESSED_DB_NAME, "system/system", g_level=2)
        for key in result.keys():
            tmp1 = 0
            tmp2 = 0
            for row2 in view_system:
                if row2.key[0] == key:
                    tmp1 += row2.value
                    if row2.key[1] == 'IOS':
                        tmp2 = row2.value

            if tmp1:
                result[key][1] = tmp2 / tmp1
                result[key][2] = 1 - tmp2/tmp1

        # get most used emoji
        create_View.create_view(server, PROCESSED_DB_NAME, "emoji_States", "_count")
        view_emojis = create_View.get_view(server, PROCESSED_DB_NAME, "emoji_States/emoji_States",
                                          g_level=2)
        for key1 in result.keys():
            dict0 = {}
            emoji_frequency = 0
            temp = ''
            for row3 in view_emojis:
                if row3.key[0] == key1:
                    dict0[row3.key[1]] = row3.value

            if dict0:
                #print(dict0)
                temp = max(dict0, key=lambda x: dict0[x])
                emoji_frequency = dict0[temp]
                result[key1][4] = temp
                result[key1][5] = emoji_frequency

    if group_level == 2:
        # get most used emoji
        # group_level = 2 for counting the times of each expression on each district in Viatoria
        create_View.create_view(server, PROCESSED_DB_NAME, "emoji_Vic", "_count")
        view_emojiv = create_View.get_view(server, PROCESSED_DB_NAME, "emoji_Vic/emoji_Vic", g_level=2)
        for key2 in result.keys():
            dict0 = {}
            emoji_frequency = 0
            temp = ''

            for row4 in view_emojiv:
                if row4.key[0] == key2:
                    #print(row4.key[1])
                    dict0[row4.key[1]] = row4.value

            if dict0:
                #print(dict0)
                temp = max(dict0, key=lambda x: dict0[x])
                emoji_frequency = dict0[temp]
                result[key2][4] = temp
                result[key2][5] = emoji_frequency


    if group_level == 3:
        # get most used emoji
        # group ==3 for counting the times of each expression on each district in Melbourne
        create_View.create_view(server, PROCESSED_DB_NAME, "emoji_Mel", "_count")
        view_emojim = create_View.get_view(server, PROCESSED_DB_NAME, "emoji_Mel/emoji_Mel", g_level=2)

        for key3 in result.keys():
            dict0 = {}
            emoji_frequency = 0
            temp = ''

            for row5 in view_emojim:
                #print(row5)
                if row5.key[0] == key3:
                    dict0[row5.key[1]] = row5.value
            if dict0:
                #print(dict0)
                temp = max(dict0, key=lambda x: dict0[x])
                emoji_frequency = dict0[temp]
                result[key3][4] = temp
                result[key3][5] = emoji_frequency

    result_db0.save(result)


if __name__ == "__main__":
    server_instance = couchdb.Server('http://admin:admin@115.146.86.21:5984/')
    if RESULT_DB_NAME in server_instance:
        del server_instance[RESULT_DB_NAME]
        result_db = server_instance.create(RESULT_DB_NAME)
    else:
        result_db = server_instance.create(RESULT_DB_NAME)

    save_result(result_db,1,server_instance)
    save_result(result_db,2, server_instance)
    save_result(result_db,3,server_instance)
    create_View.create_view(server_instance, RESULT_DB_NAME, "get_doc", None)
    view = create_View.get_view(server_instance, RESULT_DB_NAME, "get_doc/get_doc",None)
    end = time.clock() - start
    print("It is running at " + time.strftime("%Y-%m-%d %H:%M"))
    print(end)
