#!/usr/bin/env python

import configparser
import telegram
configfile_path = "../data/config.cfg"

config = configparser.ConfigParser()
config.read( configfile_path )

token = token = config["bot"]["token"]
url = config["bot"]["webhook_url"]


bot = telegram.Bot(token=token)
s = bot.setWebhook(url + "/" + token)

if s:
    print("webhook setup worked")
else:
    print("webhook setup failed")