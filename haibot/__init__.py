import logging
import configparser
from pymongo import MongoClient

CONFIGFILE_PATH = "data/config.cfg"
config = configparser.ConfigParser()
config.read( CONFIGFILE_PATH )

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot_log")

mongoclient = MongoClient(config.get("haibot","MONGO_URL"))
mongodb = mongoclient[config.get("haibot","DB_NAME")]