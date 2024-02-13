from flask import flash, render_template, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

from urllib.parse import urlsplit

from app import flask_app, forms, db, models, crud

import sqlalchemy as sa
from sqlalchemy import or_
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


@flask_app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.Login()

    # handle GET request
    if not form.validate_on_submit():
        return render_template('login.html', title='Sign In' , form=form)
    
    # handle invalid login
    user = models.User.query.filter(or_(models.User.email == form.username.data, models.User.username == form.username.data)).first()
    if not user or not user.check_password(form.password.data):
        flash('Invalid username or password')
        return redirect(url_for('login'))
    
    # handle valid login
    login_user(user, remember = form.remember_me.data)

    # handle next page
    next_page = request.args.get('next')
    if not next_page or urlsplit(next_page).netloc != '':
        next_page = url_for('index')

    return redirect(next_page)

@flask_app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@flask_app.route('/register', methods=['GET', 'POST'])
def register():

    # redirect if logged in
    if current_user.is_authenticated:
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
        
    # handle GET request
    form = forms.Register()
    if not form.validate_on_submit():
        return render_template('register.html', title='Register', form=form)

    # create User
    u = models.User(username=form.username.data, email=form.email.data)
    u.set_password(form.password.data)
    u = u.create()

    # on error
    if not u:
        flash('Oops, something went wrong. User not created.')
    else:
        flash('Congratulations, you are now a registered user!')

    return redirect(url_for('login'))