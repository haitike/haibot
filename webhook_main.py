from flask import Flask, request
from telegrambot.telegrambot import TelegramBot
import logging

CONFIGFILE_PATH = "data/config.py"
app = Flask(__name__)
app.config.from_pyfile(CONFIGFILE_PATH) #try
logging.basicConfig(level=logging.DEBUG)
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
    bot.terraria_set_on(ip=request.headers['X-Forwarded-For'])
    return "Terraria Server is On (IP: %s) (Host: %s)" % (bot.terraria_ip, bot.terraria_host)

@app.route("/"+app.config["TOKEN"]+"/server_off")
def server_off():
    bot.terraria_set_off()
    return "Terraria Server is Off"

if __name__ == '__main__':
    try:
        app.run()
    except:
        logger.exception("Finished program.")