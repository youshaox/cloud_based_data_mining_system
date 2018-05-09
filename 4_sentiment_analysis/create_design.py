"""
group 25
* Youshao Xiao - 876548
* Jiaheng Zhu - 848432
* Lina Zhou - 941539
* Haimei Liu - 895804
* Miaomiao Zhang - 895216
"""

"""
functions used to create views in couchdb
"""
import couchdb



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

    pro_db = couch['processed_data2']
    design_doc = {
        '_id': '_design/try2',
        'views': {
            'viewPD2': {
                'map': 'function(doc){emit(doc.id,doc);}'
            }
        }
    }

    pro_db.save(design_doc)


