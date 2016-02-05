from telegram import Updater

import gettext
locale_path = "locale"

translate_en = gettext.translation("telegrambot", locale_path, languages=['en'])
translate_es = gettext.translation("telegrambot", locale_path, languages=['es'])
translate_fl = gettext.translation("telegrambot", locale_path, languages=['fl'])

translate_en.install()

token_path = 'data/api.token'
f = open(token_path)
token = (f.read().strip())

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
    help_text = _("Use /settings <language/l> <es/en/fl>")
    command_args = update.message.text.split()
    if len(command_args) < 3:
        bot.sendMessage(chat_id=update.message.chat_id, text=help_text)
    else:
        if command_args[1] == "language" or "l":
            if command_args[2] == "en":
                bot.sendMessage(chat_id=update.message.chat_id, text=_("Language changed to English"))
                translate_en.install()
            elif command_args[2] == "es":
                bot.sendMessage(chat_id=update.message.chat_id, text=_("Language changed to Spanish"))
                translate_es.install()
            elif command_args[2] == "fl":
                bot.sendMessage(chat_id=update.message.chat_id, text=_("Language changed to Flavoured"))
                translate_fl.install()
            else:
                bot.sendMessage(chat_id=update.message.chat_id, text=_("Unknown language code"))
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

if __name__ == '__main__':
    main()

