#---group 25----
# Youshao Xiao - 876548
# Jiaheng Zhu - 848432
# Lina Zhou - 941539
# Haimei Liu - 895804
# Miaomiao Zhang - 895216

import couchdb
import create_View

sever_instance = couchdb.Server('http://admin:admin@XXXX.XXXX.XX.XXX:5984/')

# create_view (couch, db, map_name, reduce_name)
# get_view(couch, db, design_view_name, g_level=1):


# group_level = 1 for the number of tweets on each state
# group_level = 2 for the number of tweets on each district in Victoria
# group_level = 3 for the number of tweets on each district in Melbourne
create_View.create_view(sever_instance, "tagged_tweet", "district", "_count")
view = create_View.get_view(sever_instance, "tagged_tweet", "district/district", g_level=1)
for row in view:
    print(row)


# group_level = 1 for the accumulated value of each state
# group_level = 2 for the accumulated value of each district in Victoria
# group_level = 3 for the accumulated value of each district in Melbourne
create_View.create_view(sever_instance, "tagged_tweet", "sentiment", "_sum")
view = create_View.get_view(sever_instance, "tagged_tweet", "sentiment/sentiment", g_level=1)
for row in view:
    print(row)


#group_level = 2 for the number of each system on each state
create_View.create_view(sever_instance, "tagged_tweet", "system", "_count")
view = create_View.get_view(sever_instance, "tagged_tweet", "system/system", g_level=2)
for row in view:
    print(row)

print("--------------------------------------------------- emoji_states")
#group_level = 2 for counting the times of each expression on each state
create_View.create_view(sever_instance, "tagged_tweet", "emoji_States", "_count")
view = create_View.get_view(sever_instance, "tagged_tweet", "emoji_States/emoji_States", g_level=2)
for row in view:
    print(row)


print("--------------------------------------------------- emoji_Viatoria")
#group_level = 2 for counting the times of each expression on each district in Viatoria
create_View.create_view(sever_instance, "tagged_tweet", "emoji_Vic", "_count")
view = create_View.get_view(sever_instance, "tagged_tweet", "emoji_Vic/emoji_Vic", g_level=2)
for row in view:
    print(row)

print("--------------------------------------------------- emoji_Melbourne")
#group_level = 2 for counting the times of each expression on each district in Melbourne
create_View.create_view(sever_instance, "ptagged_tweet", "emoji_Mel", "_count")
view = create_View.get_view(sever_instance, "tagged_tweet", "emoji_Mel/emoji_Mel", g_level=2)
for row in view:
    print(row)



print("--------------------------------------------------- raw_data")

create_View.create_view(sever_instance, "raw_tweet", "process_raw", None)
view = create_View.get_view(sever_instance, "raw_tweet", "process_raw/process_raw",None)
for row in view:
    print(row)
    break

print("--------------------------------------------------- aurin")
create_View.create_view(sever_instance, "aurin_data", "get_doc", None)
view = create_View.get_view(sever_instance, "aurin_data", "get_doc/get_doc",None)
for row in view:
    print(row)


print("--------------------------------------------------- result")
create_View.create_view(sever_instance, "final_result", "get_doc", None)
view = create_View.get_view(sever_instance, "final_result", "get_doc/get_doc",None)
for row in view:
    print(row)
