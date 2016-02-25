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

    def get_autonot_status(self, id):
        autonot = self.col_autonot.find_one( {'name':"autonot" } )
        try:
            if id in autonot["users"]:
                return True
            else:
                return False
        except:
            return False

    def set_autonot_on(self, id):
        self.col_autonot.update_one({'name':"autonot"},{"$addToSet": {"users": id}},upsert=True)
        return True

    def set_autonot_off(self, id):
        self.col_autonot.update_one({'name':"autonot"},{"$pull": {"users": id}},upsert=True)
        return False

    def add_milestone(self, user=None, text=" " ):
        t_update = terraria_update.Milestone(user, text)
        self.db.create("terraria_updates", t_update)
        #self.notification(t_update.text())
        return t_update.get_text()

    def change_status(self, status, user=None, ip=None ):
        t_update = terraria_update.Status(user, status, ip)
        self.db.create("terraria_updates", t_update)
        #self.terraria_autonotification(t_update.text())
        self.last_status_update = t_update

    def notification(self, text):
        autonot = self.col_data.find_one( {'name':"autonot" } )
        if autonot:
            for i in autonot["users"]:
                try:
                    self.bot.sendMessage(chat_id=i, text=text)
                except TelegramError as e:
                    logger.warning("Terraria Autonot to User [%d]: TelegramError: %s" % (i,e))