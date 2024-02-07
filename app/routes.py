from flask import flash, render_template, redirect
from app import flask_app
from app import forms

@flask_app.route('/')
def load():
    return redirect('/index')

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

@flask_app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.Login()
    if form.validate_on_submit():
        flash(f'Login for user {form.username.data}, remeber = {form.remember_me.data}')
        return redirect('/index')
    return render_template('login.html', title='Sign In' , form=form)
