import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
import os

from . import flask_app

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

