class ListManager(object):
    def __init__(self, db):
        self.db = db
        if not self.db.exists_document("lists"):
            self.db.update_one_array_addtoset("lists", "lists", "default", upsert=True)

    def get_entries(self):
        pass

    def add_entry(self):
        pass

    def remove_entry(self):
        pass

    def mark_done_entry(self):
        pass

    def search_entries(self):
        pass

    def get_random_entry(self):
        pass

    def get_lists(self, enumerated=False):
        lists = self.db.read_one("lists")["lists"]
        if enumerated:
            return list(enumerate(lists,1))
        else:
            return lists

    def add_list(self, list_name):
        result = self.db.update_one_array_addtoset("lists", "lists", list_name, upsert=True)
        return result.modified_count # In older pymongo versions is  always None

    def delete_list(self, list_name):
        result = self.db.update_one_array_pull("lists", "lists", list_name, upsert=True)
        return result.modified_count # In older pymongo versions is always None

    def clone_list(self):
        pass

    def set_current_list(self, tel_id, list):
        result = self.db.update_one("user_data", query={"user_id":tel_id}, value_dict={"current_list":list})
        return result.modified_count # In older pymongo versions is always None

    def get_readers(self):
        cursor = self.db.read_with_projection("user_data", query={"is_reader":True},
                                              projection={"user_id":True, "user_name":True } )
        return cursor

    def add_reader(self, tel_id):
        self.db.update_one("user_data", query={"user_id":tel_id}, value_dict={"is_reader":True})

    def delete_reader(self, tel_id):
        self.db.update_one("user_data", query={"user_id":tel_id}, value_dict={"is_reader":False})

    def get_writers(self):
        cursor = self.db.read_with_projection("user_data", query={"is_writer":True},
                                              projection={"user_id":True, "user_name":True } )
        return cursor

    def add_writer(self, tel_id):
        self.db.update_one("user_data", query={"user_id":tel_id}, value_dict={"is_writer":True})

    def delete_writer(self, tel_id):
        self.db.update_one("user_data", query={"user_id":tel_id}, value_dict={"is_writer":False})

    def is_reader(self, tel_id):
        user = self.db.read_one_with_projection("user_data", query={"user_id":tel_id}, projection={"is_reader":1 , "_id":0})
        if user:
            return user["is_reader"]
        else:
            return False

    def is_writer(self, tel_id):
        user = self.db.read_one_with_projection("user_data", query={"user_id":tel_id}, projection={"is_writer":1 , "_id":0})
        if user:
            return user["is_writer"]
        else:
            return False

    def has_list(self, list_name):
        if list_name in self.get_lists():
            return True

    def user_exists(self, tel_id):
        return self.db.exists_document("user_data", query={"user_id":tel_id} )