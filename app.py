import sqlalchemy as sa
import sqlalchemy.orm as so

from app import flask_app, db
from app.models import User, Post

@flask_app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post': Post}

kwargs ={
    'port': 5000,
    'debug': True,
    'host': '0.0.0.0'
}


if __name__ == "__main__":
    flask_app.run(**kwargs)