from telegrambot.telegrambot import TelegramBot
from telegrambot.flask_config_class import Config
import logging

CONFIGFILE_PATH = "data/config.py"
config = Config(".")
config.from_pyfile(CONFIGFILE_PATH) #try
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("bot_log")

def main():
    bot = TelegramBot(config)
    bot.start_webhook_server()
    logger.info("Finished program.")

if __name__ == '__main__':
    main()