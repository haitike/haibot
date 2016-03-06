from __future__ import absolute_import
from haibot import db

COL = "lists"
if not db[COL].find().limit(1).count():
    db[COL].insert_one({"name":"default", "entries" : [] })

def get_entries(listname, mode="notdone", enumerated=False ):
    entries = []

    cursor = db[COL].find_one({"name":listname},projection={"entries":True, "_id": False})
    if cursor:
        for index, entry in enumerate(cursor["entries"], 1):
            if enumerated:
                 entry["index"] = index

            if mode == "all":
                entries.append(entry)
            elif mode == "done":
                if entry["done"] == True:
                    entries.append(entry)
            else: #notdone
                if entry["done"] == False:
                    entries.append(entry)
    return entries

def add_entry(entry, listname, user_id):
    new_entry = {"entry":entry, "done":False, "user_id":user_id}
    db[COL].update_one({"name":listname}, {"$push": {"entries" : new_entry}})

def remove_entry(entry, listname):
    pass

def set_done_entry(entry, listname):
    pass

def get_random_entry(listname):
    pass

def search_entries(expression, list=None):
    if list == None:
        "search all lists"
    else:
        "search only list"

def get_lists(enumerated=False):
    lists = []

    cursor = db[COL].find({},projection={"name":True}).sort("$natural",1)
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