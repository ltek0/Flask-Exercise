from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_user, current_user, login_required, logout_user

from app import flask_app, db
from app.forms import EditProfileForm, LoginForm, RegisterForm
from app.models import User

from urllib.parse import urlparse
from datetime import datetime as dt

@flask_app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = dt.utcnow()
        db.session.commit()


def _get_next_url_from_request(request):
    next_url = request.args.get('next', None)
    if not next_url or urlparse(next_url).netloc != urlparse(request.url).netloc:
        if request.referrer != request.url:
            return request.referrer or url_for('index')
        else:
            return  url_for('index')
    return next_url


@flask_app.route('/')
def index():
    user = current_user or None

    posts = [{
        'title': 'hello-title',
        'body': 'hello',
        'author': {'username': 'karl'}
    }]
    return render_template('index.html.j2', posts = posts, user = user)


@flask_app.route("/login", methods=['GET', 'POST'])
def login():
    next_url = _get_next_url_from_request(request)
    if current_user.is_authenticated:
        return redirect(next_url)
    if request.method == "GET":
        session['next_url'] = next_url
    else:
        next_url = session['next_url']
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(db.or_(User.email == form.username.data, User.username == form.username.data)).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Welcome Back!')
            return redirect(next_url)
        else:
            flash('Invalid username or password')
            return redirect(url_for('login', next = next_url))
    return render_template('login.html.j2', title="Sign In", form = form)


@flask_app.route('/register', methods=['GET','POST'])
def register():
    next_url = _get_next_url_from_request(request)
    if current_user.is_authenticated:
        return redirect(next_url)
    if request.method == "GET":
        session['next_url'] = next_url
    else:
        next_url = session['next_url']
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    display_name=form.display_name.data)
        user.set_password(form.password.data)
        user = user.create()
        if user:
            login_user(user, remember=False)
            flash('You are now a registered')
        else:
            flash('Something went wrong')
        return redirect(next_url)
    return render_template('register.html.j2', title='Register', form=form)


@flask_app.route('/logout')
@login_required
def logout():
    next_url = _get_next_url_from_request(request)
    if current_user.is_authenticated:
        logout_user()
        flash('You are now logged out')
    return redirect(next_url)


@flask_app.route('/user/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user:
        title = 'User: {}'.format(user.display_name)
    else:
        title = 'Not Found'
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('profile.html.j2', user=user, posts=posts, title=title)


@flask_app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(original_username=current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.display_name = form.display_name.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.display_name.data = current_user.display_name
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html.j2', title='Edit Profile', form=form)

@flask_app.route('/follow/<username>')
@login_required
def follow(username):
    current_user_profile = redirect(url_for('profile', username=current_user.username))
    user = User.query.filter_by(username = username).first()
    if not user:
        flash(f'user {username} was not found')
        return current_user_profile
    if user == current_user:
        flash(f'You cannot follow yourself')
        return current_user_profile
    current_user.follow(user)
    db.session.commit()
    flash(f'You are now following {user.display_name}')
    return redirect(url_for('profile', username=user.username))

@flask_app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    current_user_profile = redirect(url_for('profile', username=current_user.username))
    user = User.query.filter_by(username = username).first()
    if not user:
        flash(f'user {username} was not found')
        return current_user_profile
    if user == current_user:
        flash(f'You cannot unfollow yourself')
        return current_user_profile
    current_user.unfollow(user)
    db.session.commit()
    flash(f'You are no longer following {user.display_name}')
    return redirect(url_for('profile', username=user.username))