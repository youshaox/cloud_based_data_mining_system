import couchdb
import  os
import re

# This program handles the couchDB MapReduce processing
# Through the couchdb library interface. It handles the creation and modification of views,
# As well as using the views to perform sorting on the values and perform further aggregation


# Create a view in couchDB, returning a dictionary with the properties of the view
def create_view (couch, db, map_name, reduce_name):

    func_dir = os.path.dirname(os.path.realpath(__file__))+"/map_functions/"
    view_name = re.sub('.js', '', map_name)
    design_name = view_name

    # Get the database
    db2 = couch[db]

    # Reads the map function from the directory
    map_func = open(func_dir+map_name+'.js', 'r').read()

    # Reduce function
    if reduce_name == None:
        # Design Doc
        design_doc = {
            '_id': '_design/'+design_name,
            'views': {
                view_name: {
                    'map': map_func
                }
            }
        }
    else:
        if reduce_name in "_count _sum _stats":
            reduce_func = reduce_name
        else:
            reduce_func = open(reduce_name+'.js','r').read()
        # Design Doc
        design_doc = {
            '_id': '_design/'+design_name,
            'views': {
                view_name: {
                    'map': map_func,
                    'reduce': reduce_func
                }
            }
        }

    try:
        db2.save(design_doc)
    except couchdb.http.ResourceConflict:
        design = db2["_design/"+design_name]
        db2.delete(design)
        db2.save(design_doc)


# get the view
# design_view_name -- 'map_func_name/map_func_name'
def get_view(couch, db, design_view_name, g_level=1):
    database = couch[db]
    if g_level == None:
        view = database.view(design_view_name)
    else:
        view = database.view(design_view_name, group_level=g_level)
    return view
