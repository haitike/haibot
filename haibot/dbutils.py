from __future__ import absolute_import
import haibot

ASCENDING = 1
DESCENDING = -1

def create(collection, document):
    if document is not None:
        haibot.mongodb[collection].insert(document)
    else:
        raise Exception("Nothing to save, because document parameter is None")
        logger.warning("A document could not be created in MongoDB Collection: %s" % (collection))

def read(collection, query={}, document_id=None, desc_order=False, asc_order=False):
    if document_id is None:
        if desc_order:
            return haibot.mongodb[collection].find(query).sort("$natural",DESCENDING)
        elif asc_order:
            return haibot.mongodb[collection].find(query).sort("$natural",ASCENDING)
        else:
            return haibot.mongodb[collection].find(query)
    else:
        if desc_order:
            return haibot.mongodb[collection].find({"_id":document_id}).sort("$natural",DESCENDING)
        elif asc_order:
            return haibot.mongodb[collection].find({"_id":document_id}).sort("$natural",ASCENDING)
        else:
            return haibot.mongodb[collection].find({"_id":document_id})

def read_one(collection, query={}, document_id=None):
    if document_id is None:
        return haibot.mongodb[collection].find_one(query)
    else:
        return haibot.mongodb[collection].find_one({"_id":document_id})

def read_with_projection(collection, projection, query={}, document_id=None ):
    if document_id is None:
        return haibot.mongodb[collection].find(query, projection)
    else:
        return haibot.mongodb[collection].find({"_id":document_id}, projection)

def read_one_with_projection(collection, projection, query={}, document_id=None ):
    if document_id is None:
        return haibot.mongodb[collection].find_one(query, projection)
    else:
        return haibot.mongodb[collection].find_one({"_id":document_id}, projection)

def read_lastXdocuments(collection, amount, query={} ):
    return haibot.mongodb[collection].find(query).sort("$natural",DESCENDING).limit(amount)

def read_last_one(collection, query={} ):
    cursor = haibot.mongodb[collection].find(query).sort("$natural",DESCENDING).limit(1)
    return cursor[0]

def exists_document(collection, query={}, document_id=None):
    if document_id is None:
        cursor = haibot.mongodb[collection].find(query).limit(1)
    else:
        cursor = haibot.mongodb[collection].find({"_id":document_id}).limit(1)
    if cursor.count() > 0:
        return True
    else:
        return False

def update(collection, query, value_dict, upsert=False):
    x = haibot.mongodb[collection].update_many(query,{"$set": value_dict},upsert=upsert)
    return x

def update_one(collection, query, value_dict, upsert=False):
    x = haibot.mongodb[collection].update_one(query,{"$set": value_dict},upsert=upsert)
    return x

def update_byID(collection, document):
    """ Use update if the _id exists, if not use insert """
    if document is not None:
        x = haibot.mongodb[collection].save(document)
    else:
        raise Exception("Nothing to update, because project parameter is None")
        logger.warning("A document could not be updated in MongoDB Collection: %s" % (collection))
    return x

def update_one_array_addtoset(collection, array, item, query={}, upsert=False):
    x = haibot.mongodb[collection].update_one(query,{"$addToSet": {array: item}},upsert=upsert)
    return x

def update_one_array_pull(collection, array, item, query={}, upsert=False):
    x = haibot.mongodb[collection].update_one(query,{"$pull": {array: item}},upsert=upsert)
    return x

def delete_byID(collection, document):
    """ Remove the document if _id exists"""
    if document is not None:
        haibot.mongodb[collection].remove(document)
    else:
        raise Exception("Nothing to delete, because project parameter is None")
        logger.warning("A document could not be deleted in MongoDB Collection: %s" % (collection))

def create_index(collection, key, order=None):
    if order:
        haibot.mongodb[collection].create_index( [(key, order)] )
    else:
        haibot.mongodb[collection].create_index( key )