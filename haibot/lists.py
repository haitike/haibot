class ListManager(object):
    def __init__(self, db):
        self.db = db
        self.users = {}

        cursor = self.db.read_with_projection("user_data", projection={"current_list":1, "user_id":1, "user_name":1,
                                                                       "is_writer":1, "is_reader":1 , "_id":0})
        for i in cursor:
            self.users[i["user_id"]] = { "user_name" : i["user_name"],
                                        "current_list" : i["current_list"],
                                        "is_writer" : i["is_writer"],
                                        "is_reader" : i["is_reader"],
                                        }

        self.db.update_one_array_addtoset("lists", "lists", "default", upsert=True)
        self.lists = self.db.read_one("lists")["lists"]


    def show_entries(self):
        pass

    def add_entry(self):
        pass

    def remove_entry(self):
        pass

    def mark_done_entry(self):
        pass

    def search_entries(self):
        pass

    def show_random_entry(self):
        pass

    def show_lists(self):
        pass

    def add_list(self):
        pass

    def remove_list(self):
        pass

    def clone_list(self):
        pass

    def switch_current_list(self):
        pass

    def show_users(self, isWriter):
        pass

    def add_users(self, isWriter):
        pass

    def remove_users(self,isWriter):
        pass

