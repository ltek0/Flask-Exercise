from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_user, current_user, login_required, logout_user

from app import flask_app, db
from app.forms import EditProfileForm, LoginForm, RegisterForm, CreatePostForm
from app.models import User, Post

from urllib.parse import urlparse
from datetime import datetime as dt

@flask_app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.update_last_seen()


def _get_next_url_from_request(request):
    next_url = request.args.get('next', None)
    if not next_url or urlparse(next_url).netloc != urlparse(request.url).netloc:
        if request.referrer != request.url:
            return request.referrer or url_for('index')
        else:
            return  url_for('index')
    return next_url


@flask_app.route('/', methods=['GET', 'POST'])
@flask_app.route('/index', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('explore'))
    
    form = CreatePostForm()
    if current_user.is_authenticated and form.validate_on_submit():
        post = Post(
            title = form.title.data,
            body = form.body.data,
            author = current_user)
        resault = post.create()
        if resault:
            flash('Your post is live')
        else:
            flash('Something went wrong')

    page = request.args.get("page", 1, type=int)
    posts = current_user.followed_posts.filter(Post.author != current_user).paginate(page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for('index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for('index', page=posts.prev_num) if posts.prev_num else None

    return render_template("index.html.j2", title="Home", form=form, posts=posts.items, next_url=next_url, prev_url=prev_url, home=True)


@flask_app.route('/explore')
def explore():

    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for('explore', page=posts.next_num) if posts.next_num else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.prev_num else None

    for i in posts.items:
        print(i.author.username)
    return render_template("index.html.j2", title="Explore", posts=posts.items, next_url=next_url, prev_url=prev_url)


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

    logout_user()

    flash('You have been logged out')
    return redirect(next_url)


@flask_app.route('/user/<username>')
def profile(username):

    user = User.query.filter_by(username=username).first_or_404()
    title = f'User {user.display_name}' if user else 'Not Found'

    page = request.args.get("page", 1, type=int)
    posts = Post.query.filter_by(author = user).order_by(Post.timestamp.desc()).paginate(page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for('profile', page=posts.next_num) if posts.next_num else None
    prev_url = url_for('profile', page=posts.prev_num) if posts.prev_num else None

    return render_template('profile.html.j2', user=user, posts=posts, title=title, next_url=next_url, prev_url=prev_url)


@flask_app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():

    form = EditProfileForm(original_username=current_user.username)

    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.display_name = form.display_name.data
        current_user.about_me = form.about_me.data
        
        flash('Your changes have been saved.')
        return redirect(url_for('profile', username=current_user.username))

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
    
    resault = current_user.follow(user)
    if resault:
        flash(f'You are now following {user.display_name}')
    else:
        flash(f'You are already following {user.display_name} or something went wrong.')

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
    
    resault = current_user.unfollow(user)
    if resault:
        flash(f'You are no longer following {user.display_name}')
    else:
        flash(f'You are not following {user.display_name} or something went wrong.')

    return redirect(url_for('profile', username=user.username))

