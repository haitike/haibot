from flask import Flask, request
from os.path import join as joinpath
import telegram

DATA_PATH = "data"
CONFIGFILE_PATH = joinpath(DATA_PATH, "config.py")

app = Flask(__name__)
app.config.from_pyfile(CONFIGFILE_PATH) #try
bot = telegram.Bot(token=app.config["TOKEN"])  #try

@app.route("/")
def test():
    return "<strong>It's Alive!</strong>"

@app.route('/'+app.config["TOKEN"], methods=['POST'])
def webhook_handler():
    update = telegram.Update.de_json(request.get_json(force=True))
    chat_id = update.message.chat.id
    text = update.message.text#.encode('utf-8')
    bot.sendMessage(chat_id=chat_id, text=text)
    return 'ok'

if __name__ == '__main__':
    app.run()