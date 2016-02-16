from telegrambot.telegrambot import TelegramBot
from telegrambot.flask_config_class import Config
import logging

CONFIGFILE_PATH = "data/config.py"
config = Config(".")
config.from_pyfile(CONFIGFILE_PATH) #try
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot_log")

if __name__ == '__main__':
    try:
        bot = TelegramBot(config=config)
        bot.start_polling_loop()
    except:
        logger.exception("Finished program.")