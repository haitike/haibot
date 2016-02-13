#!/usr/bin/env python

import telegram
import data.config as config

token = config.TOKEN
url = config.WEBHOOK_URL

bot = telegram.Bot(token=token)
s = bot.setWebhook(url + "/" + token)

if s:
    print("webhook setup worked")
else:
    print("webhook setup failed")