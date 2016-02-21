import pytz
from .collection_utils import get_col_lastdocs
from .terraria_update import *
from pytz import timezone

class Terraria(object):
    def __init__(self,db):
        self.col_updates = db.terraria_updates
        self.col_autonot_users = db.terraria_autonot

        try:
            update = get_col_lastdocs(self.col_updates, 1, query={"is_milestone" : False})[0]
            self.last_status_update = TerrariaStatusUpdate(update["user"],update["status"], update["ip"])
        except:
            self.last_status_update = TerrariaStatusUpdate(None, False, None)

    def get_status(self):
        self.last_status_update.text()

    def get_log(self, amount, only_milestone=False):
        log_text = ""
        try:
            tzinfo = timezone(self.config["TIMEZONE"])
        except:
            tzinfo = pytz.utc

        try:
            if only_milestone:
                log_list = get_col_lastdocs(self.col_updates, amount,{"is_milestone" : True})
            else:
                log_list = get_col_lastdocs(self.col_updates, amount)

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
            return log_text
        except:
            return _("There is no Log History")

    def get_ip(self):
        last_ip = self.last_status_update.ip
        if last_ip:
            return last_ip
        else:
            return _("There is no IP")

    def get_autonot(self):
        pass

    def set_autonot(self):
        def autonot_on():
            self.col_data.update_one({'name':"autonot"},{"$addToSet": {"users": sender.id}},upsert=True)
            bot.sendMessage(chat_id=update.message.chat_id, text=sender.first_name+_(" was added to auto notifications."))
        def autonot_off():
            self.col_data.update_one({'name':"autonot"},{"$pull": {"users": sender.id}},upsert=True)
            bot.sendMessage(chat_id=update.message.chat_id, text=sender.first_name+_(" was removed from auto notifications."))

        if len(command_args) > 2:
            if command_args[2] == "on":
                autonot_on()
            elif command_args[2] == "off":
                autonot_off()
            else: bot.sendMessage(chat_id=update.message.chat_id, text="/terraria autonot\n"                                                                              "/terraria autonot on/off")
        else:
            autonot = self.col_data.find_one( {'name':"autonot" } )
            try:
                if sender.id in autonot["users"]:
                    autonot_off()
                else:
                    autonot_on()
            except:
                autonot_on()

    def add_milestone(self):
        pass
    def change_status(self):
        pass
    def notification(self):
        pass