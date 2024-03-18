import subprocess
from os import path as op


def db_migrations():
    if not op.exists(op.join(op.dirname(op.realpath(__file__)), 'migrations')):
        subprocess.run(['flask', 'db', 'init'])
    subprocess.run(['flask', 'db', 'migrate'])
    subprocess.run(['flask', 'db', 'upgrade'])