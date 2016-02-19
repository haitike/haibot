import gettext
import os, sys
import logging
import pytz
from telegram import Updater, Dispatcher, Update, Bot
from .terraria_update import *
from pytz import timezone

DEFAULT_LANGUAGE = "en_EN"
logger = logging.getLogger("bot_log")

ASCENDING = 1
DESCENDING = -1

def translation_install(translation): # Comnpability with both python 2 / 3
    kwargs = {}
    if sys.version < '3':
        kwargs['unicode'] = True
    translation.install(**kwargs)

class TelegramBot(object):
    translations = {}
    api = None

    def __init__(self, config, db, use_webhook=False):
        self.config = config
        self.db = db
        self.db_collections()

        #LANGUAGE STUFF
        self.language_list = os.listdir(self.config["LOCALE_DIR"])
        for l in self.language_list:
            self.translations[l] = gettext.translation("telegrambot", self.config["LOCALE_DIR"], languages=[l], fallback=True)
        try:
            if self.config["LANGUAGE"] in self.language_list:
                translation_install(self.translations[self.config["LANGUAGE"]])
            else:
                translation_install(self.translations[DEFAULT_LANGUAGE])
        except:
            translation_install(self.translations[DEFAULT_LANGUAGE])

        # API INICIALIZATION
        self.api = Bot(token=self.config["TOKEN"])  #try
        if use_webhook:
            self.set_webhook()
            self.dispatcher = Dispatcher(self.api,None)
        else:
            self.disable_webhook()
            self.updater = Updater(token=self.config["TOKEN"])
            self.dispatcher = self.updater.dispatcher

        self.add_handlers()

        # DB get STUFF
        update = self.get_col_lastdocs(self.col_terraria, 1, query={"is_milestone" : False})[0]
        self.terraria_last_status_update = TerrariaStatusUpdate(update["user"],update["status"], update["ip"])

    def db_collections(self):
        self.col_terraria = self.db.terraria
        self.col_list = self.db.list
        self.col_data = self.db.data

    def set_webhook(self):
        s = self.api.setWebhook(self.config["WEBHOOK_URL"] + "/" + self.config["TOKEN"])
        if s:
            logger.info("webhook setup worked")
        else:
            logger.warning("webhook setup failed")
        return s

    def disable_webhook(self):
        s = self.api.setWebhook("")
        if s:
            logger.info("webhook was disabled")
        else:
            logger.warning("webhook couldn't be disabled")
        return s

    def webhook_handler(self, request):
        update = Update.de_json(request)
        self.dispatcher.processUpdate(update)

    def start_polling_loop(self):
        self.update_queue = self.updater.start_polling()
        self.updater.idle()

    def add_handlers(self):
        self.dispatcher.addTelegramCommandHandler("start", self.command_start)
        self.dispatcher.addTelegramCommandHandler("help", self.command_help)
        self.dispatcher.addTelegramCommandHandler("terraria", self.command_terraria)
        self.dispatcher.addTelegramCommandHandler("list", self.command_list)
        self.dispatcher.addTelegramCommandHandler("search", self.command_search)
        self.dispatcher.addTelegramCommandHandler("settings",self.command_settings)
        self.dispatcher.addUnknownTelegramCommandHandler(self.command_unknown)
        #self.dispatcher.addErrorHandler(self.error_handle)

    def command_start(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text=_("Bot was initiated. Use /help for commands."))

    def command_help(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text=_(
            """Available Commands:
            /start - Iniciciate or Restart the bot
            /help - Show the command list.
            /terraria status/log/autonot/ip - Terraria options
            /list <option> <item> - Manage your lists.
            /search <engine> <word> - Search using a engine.
            /settings - Change bot options (language, etc.)"""))

    def command_terraria(self, bot, update):
        user = update.message.from_user
        help_text = _(
            """Use one of the following commands:
            /terraria status - Server status (s)
            /terraria log <number> - Show Server history (l)
            /terraria autonot - Toogle Autonotifications to user (a)
            /terraria ip - Display server IP (i)
            /terraria milestone - Add a milestone to server (m)
            /terraria on/off manually change server status""")
        command_args = update.message.text.split()
        if len(command_args) < 2:
            bot.sendMessage(chat_id=update.message.chat_id, text=help_text)
        else:
            if command_args[1] == "status" or command_args[1] == "s":
                bot.sendMessage(chat_id=update.message.chat_id, text=str(self.terraria_last_status_update))

            elif command_args[1] == "log" or command_args[1] == "l":
                query = None
                limit = 5
                log_text = ""
                try: tzinfo = timezone(self.config["TIMEZONE"])
                except: tzinfo = pytz.utc

                if len(command_args) > 2:
                    try:
                        limit = int(command_args[2])
                    except:
                        if command_args[2] == "m":
                            query = {"is_milestone" : True}
                        else:
                            bot.sendMessage(chat_id=update.message.chat_id, text=_(
                                "/terraria log <number> - Number of log entries to show\n"
                                "/terraria log m - Show only milestones"))

                for i in self.get_col_lastdocs(self.col_terraria, limit, query):
                    date = pytz.utc.localize(i["date"]).astimezone(tzinfo)
                    string_date = date.strftime("%d/%m/%y %H:%M")
                    if i["is_milestone"]:
                        log_text += _("[%s] (%s) Milestone: %s\n" % (string_date,i["user"],i["milestone_text"]))
                    else:
                        if i["status"]:
                            log_text += _("[%s] (%s) Terraria Server is On (IP:%s) \n") % ( string_date,i["user"],i["ip"])
                        else:
                            log_text += _("[%s] (%s) Terraria Server is Off\n") % ( string_date,i["user"])
                bot.sendMessage(chat_id=update.message.chat_id, text=log_text)

            elif command_args[1] == "autonot" or command_args[1] == "a":
                self.col_data.update_one({'name':"autonot"},{"$addToSet": {"users": user.id}},upsert=True)
                bot.sendMessage(chat_id=update.message.chat_id, text=user.first_name+" was added to auto notifications.")

            elif command_args[1] == "ip" or command_args[1] == "i":
                last_ip = self.terraria_last_status_update.ip
                ip_text = last_ip if last_ip else _("There is no IP")
                bot.sendMessage(chat_id=update.message.chat_id, text=ip_text)

            elif command_args[1] == "milestone" or command_args[1] == "m":
                if len(command_args) > 2:
                    milestone = self.terraria_add_milestone(user.first_name, " ".join(command_args[2:]))
                    bot.sendMessage(chat_id=update.message.chat_id, text=str(milestone))
                else:
                    bot.sendMessage(chat_id=update.message.chat_id, text=_("Use /terraria milestone <TEXT>"))

            elif command_args[1] == "on":
                if len(command_args) > 2:
                    self.terraria_change_status(True, user.first_name, command_args[2])
                else:
                    self.terraria_change_status(True, user.first_name)
                    bot.sendMessage(chat_id=update.message.chat_id, text=_("Note: You can set a IP with:"
                                                                           " /server on <your ip>" ))
                bot.sendMessage(chat_id=update.message.chat_id, text=str(self.terraria_last_status_update))

            elif command_args[1] == "off":
                self.terraria_change_status(False, user.first_name)
                bot.sendMessage(chat_id=update.message.chat_id, text=str(self.terraria_last_status_update))

            else:
                bot.sendMessage(chat_id=update.message.chat_id, text=help_text)

    def command_list(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text=_("/list <option> <item>"))

    def command_search(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text=_("/search <engine> <word>"))

    def command_settings(self, bot,update):
        languages_codes_text = _("Language codes:\n")
        for lang in self.language_list:
            languages_codes_text+= "<"+lang+"> "

        help_text = _("Use /settings language language_code\n\n" + languages_codes_text)

        command_args = update.message.text.split()
        if len(command_args) < 3:
            bot.sendMessage(chat_id=update.message.chat_id, text=help_text)
        else:
            if command_args[1] == "language" or "l":
                if command_args[2] in self.language_list:
                    bot.sendMessage(chat_id=update.message.chat_id, text=_("Language changed to %s") % (command_args[2]))
                    self.config["LANGUAGE"] =  command_args[2]
                    translation_install(self.translations[self.config["LANGUAGE"]])
                else:
                    bot.sendMessage(chat_id=update.message.chat_id, text=_("Unknown language code\n\n" + languages_codes_text))
            else:
                bot.sendMessage(chat_id=update.message.chat_id, text=help_text)

    def command_unknown(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text=_("%s is a unknown command. Use /help for available commands.") % (update.message.text))

    def terraria_change_status(self, status, user=None, ip=None ):
        t_update = TerrariaStatusUpdate(user, status, ip)
        self.col_terraria.insert(t_update.toDBCollection())
        self.terraria_autonotification(str(t_update))
        self.terraria_last_status_update = t_update

    def terraria_add_milestone(self, user=None, text=" " ):
        t_update = TerrariaMilestoneUpdate(user, text)
        self.col_terraria.insert(t_update.toDBCollection())
        self.terraria_autonotification(str(t_update))
        return t_update

    def terraria_autonotification(self, text):
        autonot = self.col_data.find_one( {'name':"autonot" } )
        if autonot:
            for i in autonot["users"]:
                self.api.sendMessage(chat_id=i, text=text)

    def get_col_lastdocs(self, col, amount, query=None):
        return col.find(query).sort("$natural",DESCENDING).limit(amount)