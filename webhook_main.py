from flask import Flask, request
from telegrambot.telegrambot import TelegramBot
from pymongo import MongoClient
import logging

CONFIGFILE_PATH = "data/config.py"
app = Flask(__name__)
app.config.from_pyfile(CONFIGFILE_PATH) #try

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot_log")

mclient = MongoClient(app.config["MONGO_URL"])
db = mclient[app.config["DB_NAME"]]

bot = TelegramBot(app.config,db,use_webhook=True)

@app.route("/")
def index_test():
    return "<strong>It's Alive!</strong>"

@app.route('/'+app.config["TOKEN"], methods=['POST'])
def webhook_handler():
    bot.webhook_handler(request.get_json(force=True))
    return "ok"

@app.route("/"+app.config["TOKEN"]+"/server_on")
def server_on():
    ip = request.headers['X-Forwarded-For'] # See TODO for IP Retrieving method
    bot.terraria_change_status(True,ip=ip)
    return "Terraria Server is On (IP: %s) (Host: %s)" % (ip, "Unknown") #See TODO for "Unknown"

@app.route("/"+app.config["TOKEN"]+"/server_off")
def server_off():
    bot.terraria_change_status(False)
    return "Terraria Server is Off"

if __name__ == '__main__':
    try:
        app.run()
    except:
        logger.critical("Flask Application couldn't start")
    mclient.close()
    logger.info("Finished program.")