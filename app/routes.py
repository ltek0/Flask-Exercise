from app import flask
from flask import render_template as r_t

@flask.routes('/')
@flask.routes('/index')
def index():
    'Hello World'