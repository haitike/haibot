A simple Telegram bot written in Python with some useful commands. You can run the bot using a polling loop or with a webhook.

Compability:
- Python 2
- Python 3

Requirements:
- python-telegram-bot
- pymongo
- pytz

Instructions:
- Raname data/config-default.cfg to data/config.cfg
- Fill the token value (talk to BodFather in telegram). If you are going to use a webhook fill the webhook_url too.
- Use webhook_main.py or polling_main.py as you prefer.

Commands implemented:
- Terraria (You can get info of a Terraria server) (You can activate/desactivate the server with the bot or with the  urls :
    https:yourweb/token/server_on  / https:yourweb/token/server_off / (With host name) https:yourweb/token/server_on?hostname
- Settings (Change bot language)