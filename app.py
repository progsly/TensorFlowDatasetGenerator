from flask import Flask, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import telegram
import config
import helpers
import main
import re
import os


# CONFIG
TOKEN = config.get('TOKEN')
HOST = config.get('HOST')

bot = telegram.Bot(TOKEN)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class DatasetGenerator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, nullable=False)
    youtube_url = db.Column(db.String(250), nullable=True)
    file_name = db.Column(db.String(250), nullable=True)
    object_name = db.Column(db.String(250), nullable=True)
    new_object_name = db.Column(db.String(250), nullable=True)
    threshold = db.Column(db.Float, nullable=True)
    iter_count = db.Column(db.Integer, nullable=True)
    result_url = db.Column(db.String(250), nullable=True)


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
    if update.message.text == '/start':
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Please send a Youtube URL for dataset generation!')
        return 'OK'

    isset_dg = DatasetGenerator.query.filter_by(chat_id=update.message.chat_id).first()
    is_new = False
    if isset_dg and (isset_dg.result_url is not None):
        dg = DatasetGenerator(chat_id=update.message.chat_id)
        db.session.add(dg)
        db.session.commit()
        del isset_dg
        isset_dg = dg
        is_new = True

    elif isset_dg is not None:
        pass
    else:
        isset_dg = DatasetGenerator(chat_id=update.message.chat_id)
        db.session.add(isset_dg)
        db.session.commit()
        is_new = True

    app.logger.info(isset_dg)
    if is_new or (isset_dg and (isset_dg.youtube_url is None)):

        try:
            youtube_url = re.search("(?P<url>https?://[^\s]+)", update.message.text).group("url")
        except Exception as e:
            youtube_url = None
            app.logger.error('Error {}'.format(e))

        if youtube_url:
            result, file_url = main.get_video(app, youtube_url)
            app.logger.info(youtube_url)
            app.logger.info(result)
            app.logger.info(file_url)

            file_name = main.download_file(file_url)
            app.logger.info(file_name)

            isset_dg.youtube_url = youtube_url
            isset_dg.file_name = file_name
            db.session.add(isset_dg)
            db.session.commit()

            bot.sendMessage(chat_id=update.message.chat_id, text='Please send a object name for detection!')

            return 'OK'

    if isset_dg and (isset_dg.object_name is None):
        isset_dg.object_name = update.message.text
        db.session.add(isset_dg)
        db.session.commit()

        bot.sendMessage(chat_id=update.message.chat_id, text='Please send a threshold for detection!')

        return 'OK'

    if isset_dg and (isset_dg.threshold is None):
        isset_dg.threshold = update.message.text
        db.session.add(isset_dg)
        db.session.commit()

        bot.sendMessage(chat_id=update.message.chat_id, text='Please send a count images!')
        return 'OK'

    if isset_dg and (isset_dg.iter_count is None):
        isset_dg.iter_count = update.message.text
        db.session.add(isset_dg)
        db.session.commit()

        bot.sendMessage(chat_id=update.message.chat_id, text='Please wait!')
        result, zip_file = main.processing(app, update.message.chat_id, isset_dg.file_name, isset_dg.object_name, isset_dg.object_name, isset_dg.iter_count, float(isset_dg.threshold))
        if result and zip_file:
            link = config.get('HOST') + '/' + zip_file
            bot.sendMessage(chat_id=update.message.chat_id, text=link)
            isset_dg.result_url = link
            db.session.add(isset_dg)
            db.session.commit()
        return 'OK'
    # main.processing(app, isset_dg.file_name, isset_dg.object_name, isset_dg.object_name, 2, isset_dg.threshold)
    bot.sendMessage(chat_id=update.message.chat_id, text='Please send a Youtube URL for dataset generation!')

    return 'OK'


@app.route('/data/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    uploads = os.path.join(app.root_path, 'data')
    return send_from_directory(directory=uploads, filename=filename)


def set_webhook():
    bot.setWebhook(url='https://%s/%s' % (HOST, TOKEN))
    db.create_all()


if __name__ == '__main__':
    set_webhook()

    app.run(port=8000, debug=True)
