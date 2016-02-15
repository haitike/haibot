from flask import Flask, request
from os.path import join as joinpath
import telegram

DATA_PATH = "data"
CONFIGFILE_PATH = joinpath(DATA_PATH, "config.py")

app = Flask(__name__)
app.config.from_pyfile(CONFIGFILE_PATH) #try
bot = telegram.Bot(token=app.config["TOKEN"])  #try

def help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="this is the help message ")

@app.route("/")
def test():
    return "<strong>It's Alive!</strong>"

@app.route('/'+app.config["TOKEN"], methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True))
    dp.processUpdate(update)
    return 'ok'

if __name__ == '__main__':
    dp = telegram.Dispatcher(bot, None)
    dp.addTelegramCommandHandler("help", help)
    app.run()