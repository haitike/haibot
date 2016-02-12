from telegram import Updater
from os.path import join as joinpath

import gettext
import configparser
import os

locale_path = "../locale/"
data_path = "../data/"
configfile_path = joinpath(data_path, "config.cfg")
default_language = "en_EN" # This is only used the first time, when data/config doesn't exist.

# Fix Python 2.x. input
try: input = raw_input
except NameError: pass

config = configparser.ConfigParser()
config.read( configfile_path )

############################ try:
token = config.get("bot","token")

translate = {}
language_list = os.listdir(locale_path)
for l in language_list:
    translate[l] = gettext.translation("telegrambot", locale_path, languages=[l], fallback=True)

current_language = default_language
############################ try:
if config.has_option("bot","language"):
    if config.get("bot","language") in language_list:
        current_language = config.get("bot","language")
translate[current_language].install()

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

if __name__ == "__main__":
    main()

