from __future__ import absolute_import
import pytz
from telegrambot import terraria_update


class Terraria(object):
    def __init__(self, db):
        self.db = db
        try:
            last_update = self.db.read_last_one("terraria_updates", query={"is_milestone" : False} )
            self.last_status_update = terraria_update.build_from_DB_document(last_update)
        except:
            self.last_status_update = terraria_update.Status(None, False, None)

        self.tzinfo = pytz.utc

    def get_status(self):
        return self.last_status_update.get_text()

    def get_log(self, amount, only_milestone=False, tzinfo=pytz.utc):
        try:
            if only_milestone:
                log_list = self.db.read_lastXdocuments("terraria_updates", amount, {"is_milestone" : True})
            else:
                log_list = self.db.read_lastXdocuments("terraria_updates", amount)
        except:
            return _("There is no Log History")
        else:
            log_text=""
            at_least_one_item = False
            for log in log_list:
                at_least_one_item = True
                log["date"] = pytz.utc.localize(log["date"]).astimezone(tzinfo)
                tmp_update = terraria_update.build_from_DB_document(log)
                log_text += tmp_update.get_text(with_date=True)+"\n"
            if at_least_one_item: return log_text
            else: return _("There is no Log History")

    def get_ip(self):
        last_ip = self.last_status_update.ip
        if last_ip:
            return last_ip
        else:
            return _("There is no IP")

    def get_autonot_status(self, telegram_id):
        autonot = self.db.read_one("data", query={'name':"autonot" })
        try:
            if telegram_id in autonot["users"]:
                return True
            else:
                return False
        except:
            return False

    def set_autonot_on(self, telegram_id):
        self.db.update_one_array_addtoset("data", {'name':"autonot"}, "users", telegram_id)
        return True

    def set_autonot_off(self, telegram_id):
        self.db.update_one_array_pull("data", {'name':"autonot"}, "users", telegram_id)
        return False

    def add_milestone(self, user=None, text=" " ):
        t_update = terraria_update.Milestone(user, text)
        self.db.create("terraria_updates", t_update)
        return t_update.get_text()

    def change_status(self, status, user=None, ip=None ):
        t_update = terraria_update.Status(user, status, ip)
        self.db.create("terraria_updates", t_update)
        self.last_status_update = t_update
        return t_update.get_text()