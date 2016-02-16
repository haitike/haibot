import gettext
import os, sys
import logging
from telegram import Updater, Dispatcher, Update

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

    def __init__(self, config):
        self.config = config
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

        #TEMPORAL
        from telegram import Bot
        self.api = Bot(token=self.config["TOKEN"])  #try

        logger.debug("TelegramBot initialized")

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

    def start_webhook(self):
        self.set_webhook()
        self.dispatcher = Dispatcher(self.api,None) #TEMPORAL
        self.add_handlers()

    def start_polling(self):
        self.disable_webhook()
        self.updater = Updater(token=self.config["TOKEN"]) # TEMPORAL
        self.dispatcher = self.updater.dispatcher
        self.add_handlers()

    def webhook_handler(self, request):
        update = Update.de_json(request)
        self.dispatcher.processUpdate(update)

    def polling_loop(self):

        # Fix Python 2.x. input
        try: input = raw_input
        except NameError: pass

        self.update_queue = self.updater.start_polling()
        while True:
            text = input("Write {stop} for stopping the bot\n")
            if text == 'stop':
                self.updater.stop()
                break
            elif len(text) > 0:
                self.update_queue.put(text)

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
            /terraria status/autonot/ip - Terraria options
            /list <option> <item> - Manage your lists.
            /search <engine> <word> - Search using a engine."""))

    def command_terraria(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text=_(
            "/terraria status\n"
            "/terraria autonot\n"
            "/terraria ip\n"))

    def command_list(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text=_("/list <option> <item>"))

    def command_search(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text=_("/search <engine> <word>"))

    def command_settings(self, bot,update):
        languages_codes_text = _("Language codes:\n")
        for lang in self.language_list:
            languages_codes_text+= "<"+lang + "> "

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


