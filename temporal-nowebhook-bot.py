from telegram import Updater

token_path = 'data/api.token'
f = open(token_path)
token = (f.read().strip())

def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='The end is near. EXTERMINATE! EXTERMINATE!')

def help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='No me cuentes tu vida, no soy tu chacha!')

def terraria(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="""/terraria status
/terraria autonot
/terraria ip""")

def lista(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="""/lista create_list
/lista remove_list
/lista add
/lista remove
/lista print
/lista print_all
/lista done""")

def quote(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="""/quote <number>
/quote search
/quote shortlist
/quote add
/quote remove""")

def etimologia(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Indica una palabra a buscar")

def evolve(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Indica una feature para implementar")

def levelup(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="PLACEHOLDER")

def unknown(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='Ese comando no existe. Usa /help [Es una sugerencia, no te ofendas conmigo :(  ] ')

def main():
    updater = Updater(token=token)
    dp = updater.dispatcher

    dp.addTelegramCommandHandler('start', start)
    dp.addTelegramCommandHandler('help', help)
    dp.addTelegramCommandHandler('terraria', terraria)
    dp.addTelegramCommandHandler('lista', lista)
    dp.addTelegramCommandHandler('quote', lista)
    dp.addTelegramCommandHandler('etimologia', lista)
    dp.addTelegramCommandHandler('evolve', lista)
    dp.addTelegramCommandHandler('levelup', lista)
    dp.addUnknownTelegramCommandHandler(unknown)

    #dp.addErrorHandler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()

