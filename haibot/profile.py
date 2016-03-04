from __future__ import absolute_import
from haibot import db

COL = "user_data"
db[COL].create_index("user_id")

##### User  #####
def get_user(id):
    user = db[COL].find_one({"user_id":id},{"_id":0})
    return user

def add_user(user_dict):
    db[COL].insert_one(user_dict)

def get_user_value(id, key):
    user = db[COL].find_one({"user_id":id},{key:1 , "_id":0})
    return user[key]

def set_user_value(id, key, value):
    result = db[COL].update_one({"user_id":id}, {"$set" : {key:value}})
    return result.modified_count # In older pymongo versions is always None

##### Many Users #####
def get_allusers(projection=None):
    if projection == None:
        return db[COL].find()
    else:
        return db[COL].find(projection=projection)

def get_users(is_key, with_name=False):
    if with_name:
        return db[COL].find({is_key:True},{"user_id":True, "user_name":True})
    else:
        return db[COL].find({is_key:True},{"user_id":True})

##### Other #####
def has_user(id):
    return db[COL].find({"user_id":id}).limit(1).count()