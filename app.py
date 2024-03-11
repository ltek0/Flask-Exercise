import subprocess
from os import path as op
from app import flask_app

kwargs ={
    'port': 5000,
    'debug': True,
    'host': '0.0.0.0'
}

if not op.exists(op.join(op.dirname(op.realpath(__file__)), 'migration')):
    subprocess.run(['flask', 'db', 'init'])
subprocess.run(['flask', 'db', 'migrate'])
subprocess.run(['flask', 'db', 'upgrade'])

if __name__ == "__main__":
    flask_app.run(**kwargs)