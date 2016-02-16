#!/usr/bin/env python

import telegram
import data.config as config

token = config.TOKEN

bot = telegram.Bot(token=token)
s = bot.setWebhook("")

if s:
    print("webhook was disabled")
else:
    print("webhook couldn't be disabled")