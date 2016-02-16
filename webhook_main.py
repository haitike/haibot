from flask import Flask, request
from os.path import join as joinpath
from telegrambot.temp_telegrambot import TelegramBot
import telegram
import logging

DATA_PATH = "data"
CONFIGFILE_PATH = joinpath(DATA_PATH, "config.py")

app = Flask(__name__)
app.config.from_pyfile(CONFIGFILE_PATH) #try

@app.route("/")
def test():
    return "<strong>It's Alive!</strong>"

@app.route('/'+app.config["TOKEN"], methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True))
    bot.dispatcher.processUpdate(update)
    return 'ok'

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("bot_log")
    try:
        bot = TelegramBot()
        bot.start_webhook()
        app.run()
    except:
        logger.exception("Finished program.")