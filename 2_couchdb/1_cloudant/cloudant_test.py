import couchdb
import cloudant

# Use CouchDB to create a CouchDB client
from cloudant.client import CouchDB
client = CouchDB(USERNAME, PASSWORD, url='http://115.146.86.138:5984')
