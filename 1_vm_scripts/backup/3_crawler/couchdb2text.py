#!/usr/bin/python
# -*- coding: UTF-8 -*-
# Created by youshaox on 27/4/18
"""
function:

"""
import couchdb


class TweetStore(object):
    def __init__(self, dbname, url='http://127.0.0.1:5984/'):
        try:
            self.server = couchdb.Server(url=url)
            self.db = self.server.create(dbname)
            self._create_views()
        except couchdb.http.PreconditionFailed:
            self.db = self.server[dbname]

def _create_views(self):
    count_map = 'function(doc) { emit(doc.id, 1); }'
    count_reduce = 'function(keys, values) { return sum(values); }'
    view = couchdb.design.ViewDefinition('twitter',
                                         'count_tweets',
                                         count_map,
                                         reduce_fun=count_reduce)
    view.sync(self.db)

    get_tweets ='function(doc) { emit(("0000000000000000000"+doc.id).slice(-19), doc); }'


if __name__ == '__main__':
    db = couchdb.Database('http://localhost:5984/tweets_source')
