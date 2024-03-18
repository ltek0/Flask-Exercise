import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

from .config import Config

flask_app = Flask(__name__)
flask_app.config.from_object(Config)

db = SQLAlchemy()
db.init_app(flask_app)
migrate = Migrate(flask_app, db)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(flask_app)

mail = Mail(flask_app)


if not flask_app.debug:
    root = logging.getLogger()
    if flask_app.config["MAIL_SERVER"]:
        auth = None
        if flask_app.config['MAIL_USERNAME'] or flask_app.config['MAIL_PASSWORD']:
            auth = (flask_app.config['MAIL_USERNAME'], flask_app.config['MAIL_PASSWORD'])
        secure = None
        if flask_app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(flask_app.config['MAIL_SERVER'], flask_app.config['MAIL_PORT']),
            fromaddr='no-reply@' + flask_app.config['MAIL_SERVER'],
            toaddrs=flask_app.config['ADMINS'], subject='Microblog Notification',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        root.addHandler(mail_handler)

    if os.path.exists('logs'):
        file_handler = RotatingFileHandler(f'logs/{__name__}.log', maxBytes=10240,backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)

        flask_app.logger.addHandler(file_handler)
        flask_app.logger.setLevel(logging.INFO)
        flask_app.logger.info('Flask App startup')


from app import models, routes, errors