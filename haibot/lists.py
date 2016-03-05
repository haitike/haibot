from __future__ import absolute_import
from haibot import db

COL = "lists"
if not db[COL].find().limit(1).count():
    db[COL].insert_one({"name":"default", "entries" : [] })

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
    lists = []

    cursor = db[COL].find({},projection={"name":True})
    for i in cursor:
        lists.append(i["name"])

    if enumerated:
        return list(enumerate(lists,1))
    else:
        return lists

def add_list(list_name):
    result = db[COL].insert_one({"name":list_name, "entries" : [] })
    return result.inserted_id

def delete_list(list_name):
    result = db[COL].delete_one({"name":list_name})
    return result.deleted_count

def clone_list(list_name):
    pass

def has_list(list_name):
    if list_name in get_lists():
        return True