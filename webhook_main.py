from telegrambot.telegrambot import TelegramBot
from telegrambot.flask_config_class import Config
from pymongo import MongoClient
import logging

CONFIGFILE_PATH = "data/config.py"
config = Config(".")
config.from_pyfile(CONFIGFILE_PATH) #try

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot_log")

mclient = MongoClient(config["MONGO_URL"])
db = mclient[config["DB_NAME"]]

bot = TelegramBot(config,db,use_webhook=True)
bot.start_webhook_server()

mclient.close()
logger.info("Finished program.")