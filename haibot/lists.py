from __future__ import absolute_import
from random import randint
from haibot import db

COL_LISTS = "lists"
COL_ENTRIES = "entries"

db[COL_LISTS].create_index("name")
db[COL_ENTRIES].create_index([("list", 1) , ("index", 1)], name="entry_index")
db[COL_ENTRIES].create_index([("owner", "text"), ("entry","text")])

if not db[COL_LISTS].find({"hidden": False}).limit(1).count():
    db[COL_LISTS].insert_one({"name":"default", "owner": "None", "index_counter": 0, "hidden": False})

if not db[COL_LISTS].find({"name":"quote"}).limit(1).count():
    db[COL_LISTS].insert_one({"name":"quote", "owner": "None", "index_counter": 0, "hidden": True})

def add_entry(entry, listname, telegram_user):
    try:
        new_index = db[COL_LISTS].find_and_modify({"name":listname}, update={"$inc" : {"index_counter" : 1}}, new=True)["index_counter"]
        new_entry = {"index":new_index, "entry":entry, "owner":telegram_user, "list":listname, "done":False}
        db[COL_ENTRIES].insert_one(new_entry)
        return new_index
    except:
        return None

def delete_entry(index, listname):
    return db[COL_ENTRIES].find_one_and_delete({"list":listname,"index":index})

def get_entry(index, listname):
    return  db[COL_ENTRIES].find_one({"list":listname,"index":index})

def get_entries(listname, mode="all"):
    entries = []

    cursor = db[COL_ENTRIES].find({"list":listname}).hint("entry_index").sort("$natural", 1)
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

def toogle_done_entry(index, listname):
    is_done = db[COL_ENTRIES].find_one({"list":listname,"index":index}, {"done":True, "_id":False})["done"]
    entry = db[COL_ENTRIES].find_one_and_update({"list":listname,"index":index}, {"$set" : {"done" : not is_done}})
    return entry, not is_done

def get_random_entry(listname):
    count = db[COL_ENTRIES].count({"list":listname})
    if count == 0:
        return None
    else:
        r = randint(0, count - 1  )
        x = db[COL_ENTRIES].find({"list":listname}).limit(-1).skip(r)
        return x[0]

def search_entries(expression, listname):
    list = []
    entries = db[COL_ENTRIES].find({"list":listname, "$text": {"$search":expression}}, {"index":True,"_id":False}).sort("index")
    for entry in entries:
        list.append(entry["index"])

    return list

def has_entry_index( index, listname):
    x = db[COL_ENTRIES].find({"list":listname,"index":index}).hint("entry_index").limit(1).count()
    return x

def add_list(listname, telegram_user="None"):
    db[COL_LISTS].insert_one({"name":listname, "owner": telegram_user, "index_counter": 0, "hidden": False })
    for i in get_lists(enumerated=True):
        if i[1] == listname:
            return i[0]

def get_lists(enumerated=False, get_hidden=False):
    lists = []

    if get_hidden:
        cursor = db[COL_LISTS].find({}, projection={"name":True,"_id":False}).sort("$natural", 1)
    else:
        cursor = db[COL_LISTS].find({"hidden": False}, projection={"name":True,"_id":False}).sort("$natural", 1)

    for i in cursor:
        lists.append(i["name"])

    if enumerated:
        return list(enumerate(lists,1))
    else:
        return lists

def delete_list(listname):
    try:
        db[COL_LISTS].delete_one({"name":listname})
        db[COL_ENTRIES].delete_many({"list":listname})
        return True
    except:
        return False

def clone_list(listname):
    pass

def toogle_hidden_list(listname):
    is_hidden = db[COL_LISTS].find_one({"name":listname}, {"hidden":True, "_id":False})["hidden"]
    db[COL_LISTS].update({"name":listname}, {"$set" : {"hidden" : not is_hidden}})
    return not is_hidden


def has_list(listname):
    if listname in get_lists(get_hidden=True):
        return True
