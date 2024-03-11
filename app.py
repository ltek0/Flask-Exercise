import subprocess
from os import path as op
from app import flask_app
kwargs ={
    'port': 5000,
    'debug': False,
    'host': '0.0.0.0'
}

if __name__ == "__main__":
    # database orm update
    if not op.exists(op.join(op.dirname(op.realpath(__file__)), 'migration')):
        subprocess.run(['flask', 'db', 'init'])
    subprocess.run(['flask', 'db', 'migrate'])
    subprocess.run(['flask', 'db', 'upgrade'])

    flask_app.run(**kwargs)

