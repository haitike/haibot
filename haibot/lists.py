from __future__ import absolute_import
from random import randint
from haibot import db

COL_LISTS = "lists"
COL_ENTRIES = "entries"

if not db[COL_LISTS].find().limit(1).count():
    db[COL_LISTS].insert_one({"name": "default", "entries" : []})

def add_entry(entry, listname, tel_id):
    new_id = db[COL_LISTS].find_and_modify({"name":listname}, update={"$inc" : {"counter_seq" : 1}}, new=True)["counter_seq"]
    new_entry = {"_id":new_id, "entry":entry, "owner_id":tel_id, "list":listname, "done":False}
    result = db[COL_ENTRIES].insert_one(new_entry)
    return result.inserted_id

def get_entries(listname, mode="all"):
    entries = []

    cursor = db[COL_ENTRIES].find({"list":listname}, projection={"owner_id":False}).sort("$natural", 1)
    if cursor:
        for index, entry in enumerate(cursor, 1):
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
    count = db[COL_ENTRIES].count({"list":listname})
    if count == 0:
        return None
    else:
        r = randint(0, count - 1  )
        x = db[COL_ENTRIES].find({"list":listname}).limit(-1).skip(r)
        return x[0]

def search_entries(expression, list=None):
    if list == None:
        "search all lists"
    else:
        "search only list"

def add_list(listname, tel_id):
    result = db[COL_LISTS].insert_one({"name":listname, "owner_id": tel_id, "counter_seq": 0 })
    return result.inserted_id

def get_lists(enumerated=False):
    lists = []

    cursor = db[COL_LISTS].find({}, projection={"name":True,"_id":False}).sort("$natural", 1)
    for i in cursor:
        lists.append(i["name"])

    if enumerated:
        return list(enumerate(lists,1))
    else:
        return lists

def delete_list(listname):
    result = db[COL_LISTS].delete_one({"name":listname})
    return result.deleted_count

def clone_list(listname):
    pass

def has_list(listname):
    if listname in get_lists():
        return True