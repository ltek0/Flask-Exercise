from app import flask_app
from flask import render_template

import logging
from logging.handlers import SMTPHandler, RotatingFileHandler

import os

@flask_app.errorhandler(404)
def page_not_found(error, message=None):
    return render_template('404.html.j2', message = message), 404

@flask_app.errorhandler(500)
def internal_error(error):
    return render_template('500.html.j2'), 500




# error logging
if not flask_app.debug:

    # use mail error logging when mail server is configured and LOG_ERROR_TO_MAIL is True
    if flask_app.config['MAIL_SERVER'] and flask_app.config['LOG_ERROR_TO_MAIL']:
        
        # check for auth username and password and construct config
        auth = None
        if flask_app.config['MAIL_USERNAME'] or flask_app.config['MAIL_PASSWORD']:
            auth = (flask_app.config['MAIL_USERNAME'], flask_app.config['MAIL_PASSWORD'])

        # from config check for MAIL_USE_TLS is True
        secure = None
        if flask_app.config['MAIL_USE_TLS']:
            secure = ()

        # setup smtp handaler
        smtp_config = {
            'mailhost'    : (flask_app.config['MAIL_SERVER'], flask_app.config['MAIL_PORT']),
            'fromaddr'    : 'no-reply@{}'.format(flask_app.config['MAIL_SERVER']),
            'toaddrs'     : flask_app.config['ADMINS'],
            'subject'     : 'Flask AppFailure',
            'credentials' : auth,
            'secure'      : secure
        }
        mail_handler = SMTPHandler(**smtp_config)
        mail_handler.setLevel(logging.ERROR)
        flask_app.logger.addHandler(mail_handler)


    # log to file if folder logs exist
    if os.path.exists('logs'):
        file_handler = RotatingFileHandler(f'logs/{__name__}.log', maxBytes=10240,backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)

        flask_app.logger.addHandler(file_handler)
        flask_app.logger.setLevel(logging.INFO)
        flask_app.logger.info('Flask App startup')


from app import models, routes, errors