from pymongo import MongoClient

ASCENDING = 1
DESCENDING = -1

class Database(object):
    """ MongoDB database and collections used in the project """

    def __init__(self, mongourl, dbname):
        self.client = MongoClient(mongourl)
        self.database = self.client[dbname]

    def create(self, collection, document):
        if document is not None:
            self.database[collection].insert(document.toDBCollection())
        else:
            raise Exception("Nothing to save, because document parameter is None")
            logger.warning("A document could not be created in MongoDB Collection: %s" % (collection))

    def read(self, collection, document_id=None, query={}):
        if document_id is None:
            return self.database[collection].find(query)
        else:
            return self.database[collection].find({"_id":document_id})

    def read_lastXdocuments(self, collection, amount, query={} ):
        return self.database[collection].find(query).sort("$natural",DESCENDING).limit(amount)

    def read_last_one(self, collection, query={} ):
        cursor = self.database[collection].find(query).sort("$natural",DESCENDING).limit(1)
        return cursor[0]

    def update(self, collection, document):
        if document is not None:
            self.database[collection].save(document.toDBCollection())
        else:
            raise Exception("Nothing to update, because project parameter is None")
            logger.warning("A document could not be updated in MongoDB Collection: %s" % (collection))

    def delete(self, collection, document):
        if document is not None:
            self.database[collection].remove(document.toDBCollection)
        else:
            raise Exception("Nothing to delete, because project parameter is None")
            logger.warning("A document could not be deleted in MongoDB Collection: %s" % (collection))