from threading import Thread

from flask import render_template
from flask_mail import Message

from . import flask_app, mail
from .models import PasswordResetTokens, User


def _send_async_email(app, msg: Message):
    with app.app_context():
        mail.send(msg)


def send_password_reset_email(user: User):
    
    expire = flask_app.config.get('PASSWORD_RESET_EXPIRE', 600)

    token = PasswordResetTokens.generate(user = user, expires_in = expire)

    email = Message(
        '[Flask Exercise] Reset Your Password',
        sender = flask_app.config['MAIL_SENDER'],
        recipients = [user.email],
        body = render_template('email/reset_password.txt.j2', user=user, token=token, expire=expire),
        html = render_template('email/reset_password.html.j2', user=user, token=token)
    )
    Thread(target=_send_async_email, args=(flask_app, email)).start()
