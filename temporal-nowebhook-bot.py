from telegram import Updater

import gettext
import configparser

locale_path = "locale"
data_path = "data/"
language_list_path= "locale/language_list"
default_language = "en" # This is only used the first time, when data/config doesn't exist. 
current_language = ""

languages = {} # Key = ISO Code, Value = Language name
translate = {} # Key = ISO Code, Value = Language Translation

# FILE STUFF (data/token  &  locale/language_list)

f = open(data_path+"token", "r")
token = (f.read().strip())
f.close()

f = open(language_list_path,"r")
language_list = f.read().splitlines()
f.close()

for line in language_list:
    l = line.split()
    languages[l[0]] = l[1]

for l in languages:
    translate[l] = gettext.translation("telegrambot", locale_path, languages=[l]) 

# CONFIG FILE STUFF

config = configparser.ConfigParser()
config.read('data/config')
if config.has_section("bot"):
    if config.has_option("bot","language"):
        config_language = config["bot"]["language"]
        if config_language in languages:
            current_language = config_language
        else:
            current_language = default_language
    else:
        current_language = default_language
else:
    current_language = default_language

# Set the language of messages
translate[current_language].install()

# FUNTIONS

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
    lcodelist_text = _("Language codes:\n")
    for l in languages:
        lcodelist_text+= l + " - " + languages[l] + "\n"

    help_text = _("Use /settings language <language_code>\n\n" + lcodelist_text)

    command_args = update.message.text.split()
    if len(command_args) < 3:
        bot.sendMessage(chat_id=update.message.chat_id, text=help_text)
    else:
        if command_args[1] == "language" or "l":
            if command_args[2] in languages:
                bot.sendMessage(chat_id=update.message.chat_id, text=_("Language changed to %s") % (languages[command_args[2]]) )
                current_language =  command_args[2]
                translate[current_language].install()
            else:
                bot.sendMessage(chat_id=update.message.chat_id, text=_("Unknown language code\n\n" + lcodelist_text))
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

    updater.start_polling()

    updater.idle()

    # SAVE CONFIG FILE HERE
if __name__ == "__main__":
    main()

