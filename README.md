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
- Fill the token value (talk to BodFather in telegram).
- If you are going to use a webhook fill the webhook_url too and add the mongodb link of your webpage too.
- Use webhook_main.py or polling_main.py as you prefer.
- You can specify in data/config.cfg the bot_owner. The owner will get some admin rights when he uses a command for first time.
  Some rights are: modify the lists or bestow rights to other users.
  You must specify your telegram ID in the config.cfg. You can get it launching the bot and using /profile.

Commands implemented:
- Terraria (You can get info of a Terraria server) (You can activate/desactivate the server with the bot or with the  urls :
    https:yourweb/token/server_on  / https:yourweb/token/server_off / (With host name) https:yourweb/token/server_on?hostname
- Lists (Manage lists)
- Quote (Manage quotes)
- Autonot (auto-notifications for: terraria milestone, terraria on, terraria off and play command  )
- Play (Notify that you are ready for playing for X hours)
- Settings (Change bot language) and Profile (users info)

Extra notes:
- You must disable /setprivacy talking with BotFather if you want to be able to add quotes to the "quote" command in groups.