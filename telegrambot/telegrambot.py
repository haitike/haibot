import gettext
import os, sys
import logging
from telegram import Updater, Dispatcher, Update, Bot
from telegram.error import *
from .terraria import *

DEFAULT_LANGUAGE = "en_EN"
logger = logging.getLogger("bot_log")

def translation_install(translation): # Comnpability with both python 2 / 3
    kwargs = {}
    if sys.version < '3':
        kwargs['unicode'] = True
    translation.install(**kwargs)

class TelegramBot(object):
    translations = {}
    bot = None

    def __init__(self, config, db, use_webhook=False):
        self.config = config
        self.collection = db.bot_data
        self.terraria = Terraria(db)

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

        # bot INICIALIZATION
        self.bot = Bot(token=self.config["TOKEN"])  #try
        if use_webhook:
            self.set_webhook()
            self.dispatcher = Dispatcher(self.bot,None)
        else:
            self.disable_webhook()
            self.updater = Updater(token=self.config["TOKEN"])
            self.dispatcher = self.updater.dispatcher

        self.add_handlers()

    def set_webhook(self):
        s = self.bot.setWebhook(self.config["WEBHOOK_URL"] + "/" + self.config["TOKEN"])
        if s:
            logger.info("webhook setup worked")
        else:
            logger.warning("webhook setup failed")
        return s

    def disable_webhook(self):
        s = self.bot.setWebhook("")
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
            /list option item - Manage your lists.
            /search engine word - Search using a engine.
            /settings - Change bot options (language, etc.)"""))

    def command_terraria(self, bot, update):
        sender = update.message.from_user
        help_text = _(
            """Use one of the following commands:
            /terraria status - Server status (s)
            /terraria log <number> - Show Server history (l)
            /terraria autonot <on/off> - Toogle Autonotifications to user (a)
            /terraria ip - Display server IP (i)
            /terraria milestone - Add a milestone to server (m)
            /terraria on/off manually change server status""")
        command_args = update.message.text.split()
        if len(command_args) < 2:
            bot.sendMessage(chat_id=update.message.chat_id, text=help_text)
        else:
            if command_args[1] == "status" or command_args[1] == "s":
                self.bot_message(update.message.chat_id, self.terraria.get_status())

            elif command_args[1] == "log" or command_args[1] == "l":
                if len(command_args) > 2:
                    try:
                        log_text = self.terraria.get_log(int(command_args[2]))
                    except:
                        if command_args[2] == "m":
                            log_text = self.terraria.get_log(5, only_milestone=True)
                        else:
                            log_text = _("/terraria log <number> - Number of log entries to show\n"
                                         "/terraria log m - Show only milestones")
                else:
                    log_text = self.terraria.get_log(5)
                self.bot_message(update.message.chat_id, log_text)

            elif command_args[1] == "autonot" or command_args[1] == "a":
                # if command_args... blabla
                self.terraria.get_autonot()
                self.terraria.set_autonot()

            elif command_args[1] == "ip" or command_args[1] == "i":
                self.bot_message(update.message.chat_id, self.terraria.get_ip())

            elif command_args[1] == "milestone" or command_args[1] == "m":
                if len(command_args) > 2:
                    milestone = self.terraria_add_milestone(sender.first_name, " ".join(command_args[2:]))
                    bot.sendMessage(chat_id=update.message.chat_id, text=milestone.text())
                else:
                    bot.sendMessage(chat_id=update.message.chat_id, text=_("Use /terraria milestone <TEXT>"))

            elif command_args[1] == "on":
                if len(command_args) > 2:
                    self.terraria_change_status(True, sender.first_name, command_args[2])
                else:
                    self.terraria_change_status(True, sender.first_name)
                    bot.sendMessage(chat_id=update.message.chat_id, text=_("Note: You can set a IP with:"
                                                                           " /server on <your ip>" ))
                bot.sendMessage(chat_id=update.message.chat_id, text=self.terraria_last_status_update.text())

            elif command_args[1] == "off":
                self.terraria_change_status(False, sender.first_name)
                bot.sendMessage(chat_id=update.message.chat_id, text=self.terraria_last_status_update.text())

            else:
                bot.sendMessage(chat_id=update.message.chat_id, text=help_text)

    def command_list(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text=_("/list option item"))

    def command_search(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text=_("/search engine word"))

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

    def bot_message(self, chat_id, text):
        try:
            self.bot.sendMessage(chat_id=chat_id, text=text)
        except:
            logger.warning("A Message could not be sent:\n%s " % (text))

    def terraria_change_status(self, status, user=None, ip=None ):
        t_update = TerrariaStatusUpdate(user, status, ip)
        self.col_terraria.insert(t_update.toDBCollection())
        self.terraria_autonotification(t_update.text())
        self.terraria_last_status_update = t_update

    def terraria_add_milestone(self, user=None, text=" " ):
        t_update = TerrariaMilestoneUpdate(user, text)
        self.col_terraria.insert(t_update.toDBCollection())
        self.terraria_autonotification(t_update.text())
        return t_update

    def terraria_autonotification(self, text):
        autonot = self.col_data.find_one( {'name':"autonot" } )
        if autonot:
            for i in autonot["users"]:
                try:
                    self.bot.sendMessage(chat_id=i, text=text)
                except TelegramError as e:
                    logger.warning("Terraria Autonot to User [%d]: TelegramError: %s" % (i,e))

    def get_col_lastdocs(self, col, amount, query=None):
        return col.find(query).sort("$natural",DESCENDING).limit(amount)