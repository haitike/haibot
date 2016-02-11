from flask import Flask, request
import telegram
import configparser

data_path = "data/"
configfile_path = data_path + "config.cfg"

# Open Config File
config = configparser.ConfigParser()
config.read( configfile_path )
if config.has_section("bot") == False:
    config.add_section("bot")

# Token
token = config["bot"]["token"]

#Flask Start
app = Flask(__name__)
app.config.from_pyfile('flaskapp.cfg')

# Bot open
global bot
bot = telegram.Bot(token=token)

# Displayed text in the website.
@app.route("/")
def test():
    return "<strong>It's Alive!</strong>"

# Webhook Handler
@app.route('/'+token, methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        # retrieve
        update = telegram.Update.de_json(request.get_json(force=True))
        chat_id = update.message.chat.id
        text = update.message.text.encode('utf-8')

        # repeat the same message back (echo)
        bot.sendMessage(chat_id=chat_id, text=text)

    return 'ok'

if __name__ == '__main__':
    app.run()
