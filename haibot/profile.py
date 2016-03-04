from __future__ import absolute_import
from haibot import dbutils

COLLECTION = "user_data"
dbutils.create_index("user_data", "user_id")


##### User  #####
def get_user(id):
    user = dbutils.read_one_with_projection("user_data", query={"user_id":id}, projection={"_id":0})
    return user

def add_user(user_dict):
    dbutils.create("user_data", user_dict)

def get_user_value(id, key):
    user = dbutils.read_one_with_projection("user_data", query={"user_id":id}, projection={key:1 , "_id":0})
    return user[key]

def set_user_value(id, key, value):
    result = dbutils.update_one("user_data", query={"user_id":id}, value_dict={key:value})
    return result.modified_count # In older pymongo versions is always None

##### Many Users #####
def get_allusers(projection=None):
    if projection == None:
        return dbutils.read("user_data")
    else:
        return dbutils.read_with_projection("user_data", projection=projection )

def get_users(is_key, with_name=False):
    if with_name:
        return dbutils.read_with_projection("user_data", query={is_key:True}, projection={"user_id":True, "user_name":True } )
    else:
        return dbutils.read_with_projection("user_data", query={is_key:True}, projection={"user_id":True} )

##### Other #####
def has_user(id):
    return dbutils.exists_document("user_data", query={"user_id":id} )