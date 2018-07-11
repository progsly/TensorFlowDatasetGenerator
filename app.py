from flask import Flask, request
import telegram
import config
import helpers
import main
import re


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

    youtube_url = re.search("(?P<url>https?://[^\s]+)", update.message.text).group("url")
    result, file_url = main.get_video(app, youtube_url)
    app.logger.info(youtube_url)
    app.logger.info(result)
    app.logger.info(file_url)

    file_name = main.download_file(file_url)
    app.logger.info(file_name)

    main.processing(app, file_name, 'train', 'train', 100, 0.5)
    bot.sendMessage(chat_id=update.message.chat_id, text='Please send a Youtube URL for dataset generation!')

    return 'OK'


def set_webhook():
    bot.setWebhook(url='https://%s/%s' % (HOST, TOKEN))


if __name__ == '__main__':
    set_webhook()

    app.run(host='0.0.0.0', port=8000, debug=True)
