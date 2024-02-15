from flask import flash, render_template, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required

from urllib.parse import urlsplit, urlparse

from app import flask_app, forms, db, models, routes_tools

import sqlalchemy as sa


@flask_app.route('/login', methods=['GET', 'POST'])
def login():
    next_url = session.get('next_url', None)
    
    if request.method == 'GET' and not next_url and not request.args.get('next'):
        if request.referrer and request.referrer != request.url:
            if urlparse(request.referrer).netloc == urlparse(request.url).netloc:
                session['next_url'] = request.referrer
            else:
                session['next_url'] = url_for('index')
        else:
            session['next_url'] = url_for('index') 
    elif urlparse(request.args.get('next')).netloc == urlparse(request.url).netloc:
        session['next_url'] = request.args.get('next')
    else:
        session['next_url'] = url_for('index')

    next_url = session.get('next_url', None)
    


    # redirect if logged in
    if current_user.is_authenticated:
        return redirect(next_url)

    form = forms.user.Login()
    # form validated
    if form.validate_on_submit():

        # attempt to get user
        # username field allow username or email
        # sa.or_ check both email and username

        user = models.User.query.filter(sa.or_(models.User.email == form.username.data, models.User.username == form.username.data)).first()
        # if user not found or password is wrong
        if not (user and user.check_password(form.password.data)):
            # return message
            flash('Invalid username or password')
            # reload login page with flashed message
            return redirect(url_for('login'))
        
        # login user
        login_user(user, remember=form.remember_me.data)
        return redirect(next_url)

    # default login page
    return render_template('login.html', form = form, title = 'Sign In')



@flask_app.route('/logout')
def logout():
    next_url = session.get('next_url', None)
    
    if request.method == 'GET' and not next_url and not request.args.get('next'):
        if request.referrer and request.referrer != request.url:
            if urlparse(request.referrer).netloc == urlparse(request.url).netloc:
                session['next_url'] = request.referrer
            else:
                session['next_url'] = url_for('index')
        else:
            session['next_url'] = url_for('index') 
    elif urlparse(request.args.get('next')).netloc == urlparse(request.url).netloc:
        session['next_url'] = request.args.get('next')
    else:
        session['next_url'] = url_for('index')

    next_url = session.get('next_url', None)
    
    
    logout_user()
    
    return redirect(next_url)



@flask_app.route('/register', methods=['GET', 'POST'])
def register():
    next_url = session.get('next_url', None)
    
    if request.method == 'GET' and not next_url and not request.args.get('next'):
        if request.referrer and request.referrer != request.url:
            if urlparse(request.referrer).netloc == urlparse(request.url).netloc:
                session['next_url'] = request.referrer
            else:
                session['next_url'] = url_for('index')
        else:
            session['next_url'] = url_for('index') 
    elif urlparse(request.args.get('next')).netloc == urlparse(request.url).netloc:
        session['next_url'] = request.args.get('next')
    else:
        session['next_url'] = url_for('index')

    next_url = session.get('next_url', None)
    
    # redirect if logged in
    if current_user.is_authenticated:
        return redirect(next_url)
    
    form = forms.user.Register()
    if form.validate_on_submit():

        # create User
        u = models.User(username=form.username.data, email=form.email.data)
        u.set_password(form.password.data)
        u = u.create() # return full user object on success, else None

        if u: # on success
            flash('Congratulations, you are now a registered user!')
            #login_user(u, remember=False)
        else: # on error
            flash('Oops, something went wrong. User not created.')

        return redirect(index)#redirect(next_url)
    
    #default action
    return render_template('register.html', title='Register', form=form)

