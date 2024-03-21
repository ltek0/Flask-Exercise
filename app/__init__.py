from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_babel import Babel

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
bootstrap = Bootstrap(flask_app)
moment = Moment(flask_app)

babel = Babel(flask_app)
@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(flask_app.config['LANGS'])

from app import models, routes, errors, log