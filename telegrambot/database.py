from pymongo import MongoClient

class Database(object):
    """ MongoDB database and collections used in the project """

    def __init__(self, mongourl, dbname):
        self.client = MongoClient(mongourl)
        self.database = self.client[dbname]

########################################################################################