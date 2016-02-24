from telegrambot.telegrambot import TelegramBot
from telegrambot.database import Database
from telegrambot.flask_config_class import Config
import logging

CONFIGFILE_PATH = "data/config.py"
config = Config(".")
config.from_pyfile(CONFIGFILE_PATH) #try
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot_log")

def main():
    database = Database(config["MONGO_URL"], config["DB_NAME"])
    bot = TelegramBot(config, db)
    bot.start_polling_loop()
    logger.info("Finished program.")

if __name__ == '__main__':
    main()