import pytz
from .utils import get_col_lastdocs
from .terraria_update import *

class Terraria(object):
    def __init__(self,db):
        self.updates_collection = db.terraria_updates
        try:
            update = get_col_lastdocs(self.updates_collection, 1, query={"is_milestone" : False})[0]
            self.last_status_update = TerrariaStatusUpdate(update["user"],update["status"], update["ip"])
        except:
            self.last_status_update = TerrariaStatusUpdate(None, False, None)

        self.tzinfo = pytz.utc

    def get_status(self):
        return self.last_status_update.text()

    def get_log(self, amount, only_milestone=False, tzinfo=pytz.utc):
        log_text = ""
        try:
            if only_milestone:
                log_list = get_col_lastdocs(self.updates_collection, amount, {"is_milestone" : True})
            else:
                log_list = get_col_lastdocs(self.updates_collection, amount)
        except:
            return _("There is no Log History")
        else:
            for i in log_list:
                date = pytz.utc.localize(i["date"]).astimezone(tzinfo)
                string_date = date.strftime("%d/%m/%y %H:%M")
                if i["is_milestone"]:
                    log_text += _("[%s] (%s) Milestone: %s\n" % (string_date,i["user"],i["milestone_text"]))
                else:
                    if i["status"]:
                        log_text += _("[%s] (%s) Terraria Server is On (IP:%s) \n") % ( string_date,i["user"],i["ip"])
                    else:
                        log_text += _("[%s] (%s) Terraria Server is Off\n") % ( string_date,i["user"])
            if log_text: return log_text
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
        t_update = TerrariaMilestoneUpdate(user, text)
        self.updates_collection.insert(t_update.toDBCollection())
        #self.notification(t_update.text())
        return t_update.text()

    def change_status(self, status, user=None, ip=None ):
        t_update = TerrariaStatusUpdate(user, status, ip)
        self.updates_collection.insert(t_update.toDBCollection())
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