from flask import render_template

from app import flask_app

@flask_app.route('/')
@flask_app.route('/index')
def index():
    posts = [
        {
            'author': {'username': 'user2'},
            'body': 'Post 1'
        },
        {
            'author': {'username': 'user3'},
            'body': 'Post 2'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)