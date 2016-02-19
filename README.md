A simple Telegram bot written in Python with some useful commands. You can run the bot using a polling loop, or with a webhook and Flask.

Compability:
- Python 2
- Python 3

Requirements:
- python-telegram-bot
- pymongo
- Flask (Only with webhook, not neccesary with polling)
- pytz

Instructions:
- Raname data/config-default.py to data/config.py.
- Fill the token value (talk to BodFather in telegram). If you are going to use a webhook fill the webhook_url too.
- Use webhook_main.py or polling_main.py as you prefer.
- Note: The config-default.py Flask and Mongo information is prepared for OpenShift. You can change it for other hosting.
