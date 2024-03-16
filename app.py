import subprocess
from os import path as op
from app import flask_app

def db_migrations():
    if not op.exists(op.join(op.dirname(op.realpath(__file__)), 'migration')):
        subprocess.run(['flask', 'db', 'init'])
    subprocess.run(['flask', 'db', 'migrate'])
    subprocess.run(['flask', 'db', 'upgrade'])

if __name__ == "__main__":
    db_migrations()
    flask_app.run(
        port=5000,
        host='0.0.0.0'
    )