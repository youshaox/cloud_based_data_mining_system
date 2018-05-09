# create view

The purpose of this part is to built views accroding to requirements of scenarios.

All map functions are stored in the folder 'map_functions'.

'create_View.py' is defined  to create views and query view. There are two functions:
    * create_view(sever, db, map_name, reduce_name)
    * get_view(sever, db, design_view_name, g_level=1)

'test_create_view.py' is used to test functions of  create_View.py. And here also shows all views will be bullt in each database in this project.

so if there is new view should be cteated, the map function should be put in this folder fist.
And then call the specify function in create_View.py.

