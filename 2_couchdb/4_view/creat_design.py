import couchdb




sever_instance=couchdb.Server('http://admin:admin@115.146.86.138:5984/')

# create design document for processed_data DB
def designdoc_processed(couch):
    processed_data_db = couch['processed_data']
    design_doc = {
        '_id':'_design/try2',
        'views':{
            'view1': {
                'map':'function(doc){emit(doc.id,doc);}'
            }
        }
    }

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



if __name__ == '__main__':

    #designdoc_geo(sever_instance)
    designdoc_aurin(sever_instance)