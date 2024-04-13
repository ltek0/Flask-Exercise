from dotenv import load_dotenv
load_dotenv('.flaskenv')

from app import flask_app
print(flask_app.config['SQLALCHEMY_DATABASE_URI'])