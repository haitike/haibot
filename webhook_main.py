from flask import Flask, request
from os.path import join as joinpath
import telegram
import configparser

data_path = "data/"
configfile_path = joinpath(data_path, "config.cfg")
flaskconfig_path = joinpath(data_path, "flaskapp.cfg")

config = configparser.ConfigParser()
config.read( configfile_path )

app = Flask(__name__)
app.config.from_pyfile(flaskconfig_path)
token = ""

@app.route("/")
def test():
    return "<strong>It's Alive!</strong>"

@app.route('/'+token)
def webhook_handler():
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True))
        chat_id = update.message.chat.id
        text = update.message.text.encode('utf-8')
        bot.sendMessage(chat_id=chat_id, text=text) # echo (temp)
    return 'ok'


if __name__ == '__main__':
    try:
        token = config.get("bot","token")
    except (configparser.NoSectionError, configparser.NoOptionError):
        print("No token found in data/config.cfg")
    else:
        bot = telegram.Bot(token=token)  #try
        app.run()