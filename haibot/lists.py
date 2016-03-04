from __future__ import absolute_import
from haibot import db

COL = "lists"
if not db[COL].find().limit(1).count():
    db[COL].update_one({},{"$addToSet":{"lists":"default"}}, upsert=True)

def get_entries(list, only_done=False):
    pass

def add_entry(entry, list):
    pass

def remove_entry(entry, list):
    pass

def set_done_entry(entry, list):
    pass

def get_random_entry(list):
    pass

def search_entries(expression, list=None):
    if list == None:
        "search all lists"
    else:
        "search only list"

def get_lists(enumerated=False):
    lists = db[COL].find_one()["lists"]
    if enumerated:
        return list(enumerate(lists,1))
    else:
        return lists

def add_list(list_name):
    result = db[COL].update_one({},{"$addToSet":{"lists":list_name}}, upsert=True)
    return result.modified_count # In older pymongo versions is  always None

def delete_list(list_name):
    result = db[COL].update_one({},{"$pull":{"lists":list_name}}, upsert=True)
    return result.modified_count # In older pymongo versions is always None

def clone_list(list_name):
    pass

def has_list(list_name):
    if list_name in get_lists():
        return True