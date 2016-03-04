from __future__ import absolute_import
import pytz
from haibot import db
from pymongo import DESCENDING
from haibot.models import TerrariaStatus, TerrariaMilestone

COL = "terraria_updates"

class Terraria(object):
    def __init__(self):
        try:
            last_update = db[COL].find_one({"is_milestone" : False}).sort("$natural", DESCENDING)
            self.last_status_update = TerrariaStatus.build_from_json(last_update)
        except:
            self.last_status_update = TerrariaStatus(None, False, None)

        self.tzinfo = pytz.utc

    def get_status(self):
        return self.last_status_update.get_update_message()

    def get_log(self, amount, only_milestone=False, tzinfo=pytz.utc):
        if only_milestone:
            log_list = db[COL].find({"is_milestone" : True}).sort("$natural", DESCENDING).limit(amount)
        else:
            log_list = db[COL].find().sort("$natural", DESCENDING).limit(amount)

        log_text=""
        at_least_one_item = False
        for log in log_list:
            at_least_one_item = True
            log["date"] = pytz.utc.localize(log["date"]).astimezone(tzinfo)
            if log["is_milestone"]:
                tmp_update = TerrariaMilestone.build_from_json(log)
            else:
                tmp_update = TerrariaStatus.build_from_json(log)
            log_text += tmp_update.get_update_message(with_date=True) + "\n"
        if at_least_one_item:
            return log_text
        else:
            return False

    def get_ip(self):
        last_ip = self.last_status_update.ip
        if last_ip:
            return last_ip
        else:
            return _("There is no IP")

    def add_milestone(self, user=None, text=" " ):
        t_update = TerrariaMilestone(user, text)
        db[COL].insert_one(t_update.to_json())
        return t_update.get_update_message()

    def change_status(self, status, user=None, ip=None ):
        t_update = TerrariaStatus(user, status, ip)
        db[COL].insert_one(t_update.to_json())
        self.last_status_update = t_update
        return t_update.get_update_message()