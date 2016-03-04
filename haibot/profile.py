from __future__ import absolute_import
from haibot import dbutils

##### User  #####
def get_user(id):
    list = dbutils.read_one_with_projection("user_data", query={"user_id":id}, projection={"_id":0})
    return list

def get_user_value(id, key):
    list = dbutils.read_one_with_projection("user_data", query={"user_id":id}, projection={key:1 , "_id":0})
    return list[key]

def set_user_value(id, key, value):
    result = dbutils.update_one("user_data", query={"user_id":id}, value_dict={key:value})
    return result.modified_count # In older pymongo versions is always None


##### Many Users #####
def get_allusers(projection=None):
    if projection == None:
        return dbutils.read("user_data")
    else:
        return dbutils.read_with_projection("user_data", projection=projection )

def get_readers():
    cursor = dbutils.read_with_projection("user_data", query={"is_reader":True},
                                          projection={"user_id":True, "user_name":True } )
    return cursor

def get_writers():
    cursor = dbutils.read_with_projection("user_data", query={"is_writer":True},
                                          projection={"user_id":True, "user_name":True } )
    return cursor

##### Other #####
def has_user(id):
    return dbutils.exists_document("user_data", query={"user_id":id} )