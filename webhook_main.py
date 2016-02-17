from flask import Flask, request
from telegrambot.telegrambot import TelegramBot
import logging

CONFIGFILE_PATH = "data/config.py"
app = Flask(__name__)
app.config.from_pyfile(CONFIGFILE_PATH) #try
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot_log")
bot = TelegramBot(config=app.config,use_webhook=True)

@app.route("/")
def index_test():
    return "<strong>It's Alive!</strong>"

@app.route('/'+app.config["TOKEN"], methods=['POST'])
def webhook_handler():
    bot.webhook_handler(request.get_json(force=True))
    return "ok"

@app.route("/"+app.config["TOKEN"]+"/server_on")
def server_on():
    bot.terraria_on(request.headers['X-Forwarded-For'])
    return "Terraria Server is On (IP: %s)" % (bot.terraria_ip)

@app.route("/"+app.config["TOKEN"]+"/server_off")
def server_off():
    bot.terraria_off()
    return "Terraria Server is Off"

if __name__ == '__main__':
    try:
        app.run()
    except:
        logger.exception("Finished program.")