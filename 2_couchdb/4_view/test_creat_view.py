import couchdb
import create_View

sever_instance = couchdb.Server('http://admin:admin@115.146.86.138:5984/')

# create_view (couch, db, map_name, reduce_name)
# get_view(couch, db, design_view_name, g_level=1):


# group_level = 1 for the number of tweets on each state
# group_level = 2 for the number of tweets on each district in Victoria
# group_level = 3 for the number of tweets on each district in Melbourne
create_View.create_view(sever_instance, "processed_data_new_system", "district", "_count")
view = create_View.get_view(sever_instance, "processed_data_new_system", "district/district", g_level=1)

for row in view:
    print(row)


# group_level = 1 for the accumulated value of each state
# group_level = 2 for the accumulated value of each district in Victoria
# group_level = 3 for the accumulated value of each district in Melbourne
create_View.create_view(sever_instance, "processed_data_new_system", "sentiment", "_sum")
view = create_View.get_view(sever_instance, "processed_data_new_system", "sentiment/sentiment", g_level=1)
for row in view:
    print(row)


#group_level = 2 for the number of each system on each state
create_View.create_view(sever_instance, "processed_data_new_system", "system", "_count")
view = create_View.get_view(sever_instance, "processed_data_new_system", "system/system", g_level=2)
for row in view:
    print(row)


create_View.create_view(sever_instance, "raw_tweets", "process_raw", None)
view = create_View.get_view(sever_instance, "raw_tweets", "process_raw/process_raw",None)
for row in view:
    print(row)
    break


create_View.create_view(sever_instance, "aurin", "get_doc", None)
view = create_View.get_view(sever_instance, "aurin", "get_doc/get_doc",None)
for row in view:
    print(row)

