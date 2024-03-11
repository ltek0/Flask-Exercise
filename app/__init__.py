from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from app.config import Config

flask_app = Flask(__name__)
flask_app.config.from_object(Config)

db = SQLAlchemy()
db.init_app(flask_app)
migrate = Migrate(flask_app, db)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(flask_app)

from app import routes, model, errors, logging