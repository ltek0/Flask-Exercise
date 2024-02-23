from urllib.parse import urlparse
from flask import flash, render_template, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user

from app import flask_app, db
from app.models import User, Post
from app.forms import user as user_form

import sqlalchemy as sa


from datetime import datetime as dt
 
def get_next_url_from_request(request):

    # check for next url in args
    next_url = request.args.get('next', None)

    #if not present or domain not the same
    if not next_url or urlparse(next_url).netloc != urlparse(request.url).netloc:

        # if not the same as current url
        if request.referrer != request.url:
            # return index if treferrer is empty 
            return request.referrer or url_for('index')

        else:
            # request.referrer same
            return  url_for('index')

    # has next url and checks out
    return next_url


@flask_app.before_request
def before_request():
    # update last seen
    if current_user.is_authenticated:
        current_user.update_last_seen(dt)


@flask_app.route('/login', methods=['GET', 'POST'])
def login():

    next_url = get_next_url_from_request(request)
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
    return render_template('user/login.html.j2', form = form, title = 'Sign In')



@flask_app.route('/logout')
def logout():
    next_url = get_next_url_from_request(request)
    logout_user()
    return redirect(next_url)



@flask_app.route('/register', methods=['GET', 'POST'])
def register():

    next_url = get_next_url_from_request(request)
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
        user_data = {
            'username': form.username.data,
            'display_name': form.display_name.data if form.display_name.data else None,
            'bio': form.bio.data if form.bio.data else None,
            'email': form.email.data,
            'password': form.password.data
        }
        u = User(**user_data)
        u = u.create() # return full user object on success, else None

        if u: # on success
            flash('Congratulations, you are now a registered user!')
            login_user(u, remember=False)
        else: # on error
            flash('Oops, something went wrong. User not created.')
        
        return redirect(next_url)
    
    # default action
    return render_template('user/register.html.j2', title='Register', form=form)


@flask_app.route('/u/<username>')
def user(username):
    # get user, if not found return 404
    user = User.query.filter_by(username = username).first_or_404()    
    
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    # get user posts if user exist
    #posts = Post.query.filter_by(author = user).all() if user else []
    return render_template('user/user.html.j2', user=user, posts=posts, current_user = current_user)


@flask_app.route('/u/<username>/edit', methods=['GET', 'POST'])
def edit_profile(username):

    next_url = get_next_url_from_request(request)
    # redirect to login with edit profile as next url
    if not current_user.is_authenticated:
        return redirect(url_for('login', next = next_url(url_for('edit_profile', username = username))))
    
    # if logged in user is not the user being edited
    if current_user.username != username:
        return redirect(url_for('user', username = current_user.username))

    # bug fix for when user login faild GET request overwrites next_url
    # save next url on first get methoad
    # On post request load next url from session
    if request.method == "GET":
        session['next_url'] = next_url
    else:
        next_url = session['next_url']

    form = user_form.EditProfile()
    if form.validate_on_submit():

        # update user
        current_user.display_name = form.display_name.data
        current_user.bio = form.bio.data
        db.session.commit()

        flash('Your changes have been saved.')
        return redirect(f'/u/{current_user.username}')
    
    # on form load
    elif request.method == 'GET':
        form.display_name.data = current_user.display_name
        form.bio.data = current_user.bio

    return render_template('user/edit.html.j2', title='Edit Profile', form = form, current_user = current_user)
