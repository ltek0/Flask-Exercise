from flask import flash, render_template, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required

from urllib.parse import urlsplit

import sqlalchemy as sa

from app import flask_app, forms, db, models

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
        user = db.session.query(models.User).filter(sa.or_(models.User.email == form.username.data, models.User.username == form.username.data)).first()
        if not user or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        
        flash(f'Login for user {form.username.data}, remeber = {form.remember_me.data}')
        login_user(user, remember = form.remember_me.data)

        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)
    
    return render_template('login.html', title='Sign In' , form=form)

@flask_app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@flask_app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.Register()
    if form.validate_on_submit():
        u = models.User(username=form.username.data, email=form.email.data)
        u.set_password(form.password.data)
        u = u.create()
        if not u:
            flash('Oops, something went wrong. User not created.')
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)