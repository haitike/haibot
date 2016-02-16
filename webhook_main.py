from flask import Flask, request
from telegrambot.telegrambot import TelegramBot
import logging

CONFIGFILE_PATH = "data/config.py"
app = Flask(__name__)
app.config.from_pyfile(CONFIGFILE_PATH) #try
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot_log")

@app.route("/")
def index_test():
    return "<strong>It's Alive!</strong>"

@app.route('/'+app.config["TOKEN"], methods=['POST'])
def webhook_handler():
    bot.webhook_handler(request.get_json(force=True))
    return 'ok'

if __name__ == '__main__':
    try:
        bot = TelegramBot(config=app.config,use_webhook=True)
        app.run()
    except:
        logger.exception("Finished program.")