from app import flask_app
import subprocess
from os import path as op

if __name__ == "__main__":
    
    if not op.exists(op.join(op.dirname(op.realpath(__file__)), 'migrations')):
        subprocess.run(['flask', 'db', 'init'])
    subprocess.run(['flask', 'db', 'migrate'])
    subprocess.run(['flask', 'db', 'upgrade'])

    flask_app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True
    )