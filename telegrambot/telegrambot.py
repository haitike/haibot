import gettext
import os, sys
import logging
from telegram import Updater, Dispatcher, Update, Bot

DEFAULT_LANGUAGE = "en_EN"
logger = logging.getLogger("bot_log")

def translation_install(translation): # Comnpability with both python 2 / 3
    kwargs = {}
    if sys.version < '3':
        kwargs['unicode'] = True
    translation.install(**kwargs)

class TelegramBot(object):
    translations = {}
    api = None
    terraria_status = False
    terraria_ip = None
    terraria_host = None

    def __init__(self, config,use_webhook=False):
        self.config = config

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
        help_text = _(
            """Use one of the following commands:
            /terraria status - Server status (s)
            /terraria log - Show Server history (l)
            /terraria autonot - Toogle Autonotifications to user (a)
            /terraria ip - Display server IP (i)
            /terraria milestone - Add a milestone to server (m)
            /terraria on/off manually change server status""")
        command_args = update.message.text.split()
        if len(command_args) < 2:
            bot.sendMessage(chat_id=update.message.chat_id, text=help_text)
        else:
            if command_args[1] == "status" or command_args[1] == "s":
                if self.terraria_status:
                    bot.sendMessage(chat_id=update.message.chat_id, text=_("Terraria server is On (IP:%s) (Host:%s)") %
                                                                          (self.terraria_ip, self.terraria_host))
                else:
                    bot.sendMessage(chat_id=update.message.chat_id, text=_("Terraria server is Off"))
            elif command_args[1] == "log" or command_args[1] == "l":
                bot.sendMessage(chat_id=update.message.chat_id, text=_("placeholder log text"))
            elif command_args[1] == "autonot" or command_args[1] == "a":
                bot.sendMessage(chat_id=update.message.chat_id, text=_("placeholder autonot text"))
            elif command_args[1] == "ip" or command_args[1] == "i":
                ip_text = self.terraria_ip if self.terraria_ip else _("There is no IP")
                bot.sendMessage(chat_id=update.message.chat_id, text=ip_text)
            elif command_args[1] == "on":
                if len(command_args) > 2:
                    self.terraria_set_on(host=update.message.from_user.first_name, ip=command_args[2])
                    bot.sendMessage(chat_id=update.message.chat_id, text=_("Server was set On by %s (IP:%s)") %
                                                                          (self.terraria_host, self.terraria_ip))
                else:
                    self.terraria_set_on(host=update.message.from_user.first_name)
                    bot.sendMessage(chat_id=update.message.chat_id, text=_("Server was set On by %s\n*You can set a IP with:"
                                                                           " /server on <your ip>" % (self.terraria_host)))
            elif command_args[1] == "off":
                self.terraria_set_off()
                bot.sendMessage(chat_id=update.message.chat_id, text=_("Terraria Server Status changed to Off"))
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

    def terraria_set_on(self, ip=None, host="Anon"):
        self.terraria_status = True
        self.terraria_ip = ip
        self.terraria_host = host

    def terraria_set_off(self):
        self.terraria_status = False
        self.terraria_ip = None
        self.terraria_host = None