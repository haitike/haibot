from telegram import Updater, Dispatcher
from os.path import join as joinpath
import data.config as config

import gettext
import os
import logging

LOCALE_PATH = "locale"
DEFAULT_LANGUAGE = "en_EN" # This is only used the first time, when data/config doesn't exist.

# Fix Python 2.x. input
try: input = raw_input
except NameError: pass

translate = {}
language_list = os.listdir(LOCALE_PATH)
for l in language_list:
    translate[l] = gettext.translation("telegrambot", LOCALE_PATH, languages=[l], fallback=True)

current_language = DEFAULT_LANGUAGE
############################ try:
#if config.has_option("bot","language"):
#    if config.get("bot","language") in language_list:
#        current_language = config.get("bot","language")
translate[current_language].install()

logger = logging.getLogger("bot_log")

def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=_("Bot was initiated. Use /help for commands."))

def help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=_("""Available Commands:
/start - Iniciciate or Restart the bot
/help - Show the command list.
/terraria status/autonot/ip - Terraria options
/list <option> <item> - Manage your lists.
/search <engine> <word> - Search using a engine."""))

def terraria(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=_("""/terraria status
/terraria autonot
/terraria ip"""))

def list(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=_("/list <option> <item>"))

def search(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=_("/search <engine> <word>"))

def settings(bot,update):
    languages_codes_text = _("Language codes:\n")
    for lang in language_list:
        languages_codes_text+= lang + " "

    help_text = _("Use /settings language <language_code>\n\n" + languages_codes_text)

    command_args = update.message.text.split()
    if len(command_args) < 3:
        bot.sendMessage(chat_id=update.message.chat_id, text=help_text)
    else:
        if command_args[1] == "language" or "l":
            if command_args[2] in language_list:
                bot.sendMessage(chat_id=update.message.chat_id, text=_("Language changed to %s") % (command_args[2]))
                global current_language
                current_language =  command_args[2]
                translate[current_language].install()

            else:
                bot.sendMessage(chat_id=update.message.chat_id, text=_("Unknown language code\n\n" + languages_codes_text))
        else:
            bot.sendMessage(chat_id=update.message.chat_id, text=help_text)

def unknown(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=_("%s is a unknown command. Use /help for available commands.") % (update.message.text))

def main():
    updater = Updater(token=token)
    dp = updater.dispatcher

    dp.addTelegramCommandHandler("start", start)
    dp.addTelegramCommandHandler("help", help)
    dp.addTelegramCommandHandler("terraria", terraria)
    dp.addTelegramCommandHandler("list", list)
    dp.addTelegramCommandHandler("search", search)
    dp.addTelegramCommandHandler("settings",settings)
    dp.addUnknownTelegramCommandHandler(unknown)
    #dp.addErrorHandler(error)

    update_queue = updater.start_polling()
    while True:
        text = input("Write {stop} for stopping the bot\n")
        if text == 'stop':
            updater.stop()
            break
        elif len(text) > 0:
            update_queue.put(text)  # Put command into queue

    ############################ try:
    config.set('bot', 'language', current_language)
    with open(configfile_path, 'w') as configfile:    # save
        config.write(configfile)

class TelegramBot(object):
    def __init__(self):
        logger.debug("TelegramBot initialized")

    def start_webhook(self):
        from telegram import Bot
        bot = Bot(token=config.TOKEN)  #try
        self.dispatcher = Dispatcher(bot,None)
        self.add_handlers()

    def start_looping(self):
        pass

    def polling_loop(self):
        pass

    def add_handlers(self):
        self.dispatcher.addTelegramCommandHandler("help", self.command_help)

    def command_help(self, bot, update):
        bot.sendMessage(chat_id=update.message.chat_id, text=_(
            """Available Commands:
            /start - Iniciciate or Restart the bot
            /help - Show the command list.
            /terraria status/autonot/ip - Terraria options
            /list <option> <item> - Manage your lists.
            /search <engine> <word> - Search using a engine."""))

