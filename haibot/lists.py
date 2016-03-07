from __future__ import absolute_import
from haibot import db

COL_LISTS = "lists"
COL_ENTRIES = "entries"

if not db[COL_LISTS].find().limit(1).count():
    db[COL_LISTS].insert_one({"name": "default", "entries" : []})

def add_entry(entry, listname, tel_id):
    new_entry = {"entry":entry, "owner_id":tel_id, "list":listname, "done":False}
    result = db[COL_ENTRIES].insert_one(new_entry)
    return result.inserted_id

def get_entries(listname, mode="all", enumerated=False ):
    entries = []

    cursor = db[COL_ENTRIES].find({"list":listname}, projection={"owner_id":False}).sort("$natural", 1)
    if cursor:
        for index, entry in enumerate(cursor, 1):
            if enumerated:
                 entry["index"] = index

            if mode == "notdone":
                if entry["done"] == False:
                    entries.append(entry)
            elif mode == "done":
                if entry["done"] == True:
                    entries.append(entry)
            else: #all
                entries.append(entry)

    return entries

def delete_entry(entry_id):
    result = db[COL_ENTRIES].delete_one({"_id":entry_id})
    return result.deleted_count

def toogle_done_entry(entry_id):
    is_done = db[COL_ENTRIES].find_one({"_id":entry_id}, {"done":True, "_id":False})["done"]
    db[COL_ENTRIES].update_one({"_id":entry_id}, {"$set" : {"done" : not is_done}})
    return not is_done

def get_random_entry(listname):
    pass

def search_entries(expression, list=None):
    if list == None:
        "search all lists"
    else:
        "search only list"

def get_lists(enumerated=False):
    lists = []

    cursor = db[COL_LISTS].find({}, projection={"name":True,"_id":False}).sort("$natural", 1)
    for i in cursor:
        lists.append(i["name"])

    if enumerated:
        return list(enumerate(lists,1))
    else:
        return lists

def add_list(listname, tel_id):
    result = db[COL_LISTS].insert_one({"name":listname, "owner_id": tel_id})
    return result.inserted_id

def delete_list(listname):
    result = db[COL_LISTS].delete_one({"name":listname})
    return result.deleted_count

def clone_list(listname):
    pass

def has_list(listname):
    if listname in get_lists():
        return True