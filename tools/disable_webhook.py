#!/usr/bin/env python

import configparser
import telegram
configfile_path = "../data/config.cfg"

config = configparser.ConfigParser()
config.read( configfile_path )

token = config.get("bot","token")
url = config.get("bot","webhook_url")

bot = telegram.Bot(token=token)
s = bot.setWebhook("")

if s:
    print("webhook was disabled")
else:
    print("webhook couldn't be disabled")