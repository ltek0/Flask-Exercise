from flask import flash, render_template, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user

from app import flask_app, routes_tools
from app.models import User
from app.forms import user as user_form

import sqlalchemy as sa


@flask_app.route('/login', methods=['GET', 'POST'])
def login():

    next_url = routes_tools.get_next_url_from_request(request)
    # redirect if logged in
    if current_user.is_authenticated:
        return redirect(next_url)
    
    # bug fix for when user login faild GET request overwrites next_url
    # save next url on first get methoad
    # On post request load next url from session
    if request.method == "GET":
        session['next_url'] = next_url
    else:
        next_url = session['next_url']

    form = user_form.Login()
    if form.validate_on_submit():

        # attempt to get user
        # username field allow username or email
        # sa.or_ check both email and username

        user = User.query.filter(sa.or_(User.email == form.username.data, User.username == form.username.data)).first()
        # user exist and password corrct
        if user and user.check_password(form.password.data):
            # login user
            login_user(user, remember=form.remember_me.data)
            return redirect(next_url)
        else:
            flash('Invalid username or password')
            # reload login page with flashed message
            return redirect(url_for('login', next = next_url))
        

    # default page / GET request
    return render_template('login.html', form = form, title = 'Sign In')



@flask_app.route('/logout')
def logout():
    next_url = routes_tools.get_next_url_from_request(request)
    logout_user()
    return redirect(next_url)



@flask_app.route('/register', methods=['GET', 'POST'])
def register():


    next_url = routes_tools.get_next_url_from_request(request)
    # redirect if logged in
    if current_user.is_authenticated:
        return redirect(next_url)
    
    # bug fix for when user login faild GET request overwrites next_url
    # no next from referrer when methoad is POST
    if request.method == "GET":
        session['next_url'] = next_url
    else:
        next_url = session['next_url']

    form = user_form.Register()
    if form.validate_on_submit():

        # create User
        u = User(username=form.username.data, email=form.email.data)
        u.set_password(form.password.data)
        u = u.create() # return full user object on success, else None

        if u: # on success
            flash('Congratulations, you are now a registered user!')
            login_user(u, remember=False)
        else: # on error
            flash('Oops, something went wrong. User not created.')
        
        return redirect(next_url)
    
    # default action
    return render_template('register.html', title='Register', form=form)

