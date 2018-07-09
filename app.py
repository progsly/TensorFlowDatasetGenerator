from flask import Flask, request
import telegram
import config
import helpers
import main


# CONFIG
TOKEN = config.get('TOKEN')
HOST = config.get('HOST')

bot = telegram.Bot(TOKEN)
app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello!'


@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    data = request.get_json(force=True)
    app.logger.info(data)

    update = telegram.update.Update.de_json(request.get_json(force=True), bot)

    if update.message.text == '/help':
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=helpers.help_text())
        return 'OK'

    bot.sendMessage(chat_id=update.message.chat_id, text='Please send a photo for recognition!')

    return 'OK'


def set_webhook():
    bot.setWebhook(url='https://%s/%s' % (HOST, TOKEN))


if __name__ == '__main__':
    set_webhook()

    app.run(host='0.0.0.0', port=8000, debug=True)
