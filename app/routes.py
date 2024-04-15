from flask import render_template, flash, redirect, url_for, request, abort, g
from flask_login import login_user, current_user, login_required, logout_user
from flask_babel import _, get_locale

from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from datetime import datetime as dt, UTC
from hashlib import sha256, md5

from . import flask_app, db, forms
from .models import User, Post, PasswordResetTokens
from .email import send_password_reset_email

import app.models as models
import app.google_cloud as google_cloud


def _get_next_url_from_request(request):
    next_url = request.args.get('next', None)
    if not next_url or urlparse(next_url).netloc != '':
        if request.referrer != request.url and not urlparse(request.referrer).netloc != urlparse(request.url).netloc:
            return request.referrer or url_for('index')
    return next_url


@flask_app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = dt.now(UTC)
        db.session.commit()
    g.locale = str(get_locale())


@flask_app.route('/', methods=['GET', 'POST'])
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('explore'))
    form = forms.CreatePostForm()
    if form.validate_on_submit():
        post = Post(
            title = form.title.data,
            body = form.body.data,
            author = current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is live'))
        # after form submit, redirect, otherwise, form data will not be cleared
        return redirect(url_for('index'))
    page = request.args.get("page", 1, type=int)
    posts = current_user.followed_posts().paginate(page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for('index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for('index', page=posts.prev_num) if posts.prev_num else None
    return render_template("index.html.j2", title="Home", form=form, posts=posts.items, next_url=next_url, prev_url=prev_url, home=True)


@flask_app.route('/explore')
def explore():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for('explore', page=posts.next_num) if posts.next_num else None
    prev_url = url_for('explore', page=posts.prev_num) if posts.prev_num else None
    return render_template("index.html.j2", title="Explore", posts=posts.items, next_url=next_url, prev_url=prev_url)


@flask_app.route('/explore/<int:post_id>')
def explore_post(post_id: int):
    # TODO: create page for posts to allow comments
    pass


@flask_app.route("/login", methods=['GET', 'POST'])
def login():
    next_url = _get_next_url_from_request(request)
    if current_user.is_authenticated:
        return redirect(next_url)
    form = forms.LoginForm()
    if form.validate_on_submit():
        u = User.query.filter(db.or_(User.email == form.username.data, User.username == form.username.data)).first()
        if not u and not u.check_password(form.password.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('login'))
        login_user(u, remember=form.remember_me.data)
        flash(_('Welcome Back!'))
        return redirect(url_for('index'))
    return render_template('user/login.html.j2', title="Sign In", form=form)


@flask_app.route('/register', methods=['GET','POST'])
def register():
    next_url = _get_next_url_from_request(request)
    if current_user.is_authenticated:
        return redirect(next_url)
    form = forms.RegisterForm()
    if form.validate_on_submit():
        u = User(username = form.username.data,
                    email = form.email.data,
                    display_name = form.display_name.data)
        u.set_password(form.password.data)
        db.session.add(u)
        db.session.commit()
        flash(_('You are now a registered'))
        return redirect(url_for('login'))
    return render_template('user/register.html.j2', title='Register', form=form)


@flask_app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(_('You have been logged out'))
    return redirect(url_for('login'))


@flask_app.route('/user/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    title = _('User  %(dn)s', dn=user.display_name) if user else _('Not Found')
    page = request.args.get("page", 1, type=int)
    posts = Post.query.filter_by(author = user).order_by(Post.timestamp.desc()).paginate(page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for('profile', page=posts.next_num, username=username) if posts.next_num else None
    prev_url = url_for('profile', page=posts.prev_num, username=username) if posts.prev_num else None
    return render_template('user/profile.html.j2', user=user, posts=posts, title=title, next_url=next_url, prev_url=prev_url)


@flask_app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = forms.EditProfileForm(original_username=current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.display_name = form.display_name.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.display_name.data = current_user.display_name
        form.about_me.data = current_user.about_me
    return render_template('user/edit_profile.html.j2', title='Edit Profile', form=form)


@flask_app.route('/change_password')
def change_password():
    #TODO: change password
    pass


@flask_app.route("/reset_password", methods=['GET', 'POST'])
def reset_password_request():
    next_url = _get_next_url_from_request(request)
    if current_user.is_authenticated:
        return redirect(next_url)
    form = forms.ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(_('An email will be sent to you shortly if the email is found in our records'))
        return redirect(url_for('login'))
    return render_template('user/reset_password.html.j2', title="Reset Password", form=form)


@flask_app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token: str):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if not PasswordResetTokens.validate(token=token):
        return abort(403, description=_("Invalid access token"))
    form = forms.ResetPasswordForm()
    if form.validate_on_submit():
        user = PasswordResetTokens.use(token=token)
        if not user:
            flash(_('Invalid or expired token'))
            return redirect(url_for('login'))
        user.set_password(form.password.data)
        db.session.commit()
        flash(_('Your password has been reset.'))
        return redirect(url_for('login'))
    return render_template('user/reset_password.html.j2', title="Reset Password", form=form)


@flask_app.route('/follow/<username>')
@login_required
def follow(username: str):
    current_user_profile = redirect(url_for('profile', username=current_user.username))
    user = User.query.filter_by(username = username).first()
    if not user:
        flash(_('user %(u)s was not found', u=username))
        return current_user_profile
    if user == current_user:
        flash(_('You cannot follow yourself'))
        return current_user_profile
    current_user.follow(user)
    flash(_('You are now following %(dn)s', dn=user.display_name))
    return redirect(url_for('profile', username=user.username))


@flask_app.route('/unfollow/<username>')
@login_required
def unfollow(username: str):
    current_user_profile = redirect(url_for('profile', username=current_user.username))
    user = User.query.filter_by(username = username).first()
    if not user:
        flash(_('user %(n)s was not found', n=username))
        return current_user_profile
    if user == current_user:
        flash(_('You cannot unfollow yourself'))
        return current_user_profile
    current_user.unfollow(user)
    flash(_('You are no longer following %(a)s', a=user.display_name))
    return redirect(url_for('profile', username=user.username))


@flask_app.route('/gallery/p')
@flask_app.route('/gallery')
def gallery():
    page = request.args.get("page", 1, type=int)
    posts = models.GalleryPost.query.order_by(models.GalleryPost.timestamp.desc()).paginate(page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for('gallery', page=posts.next_num) if posts.next_num else None
    prev_url = url_for('gallery', page=posts.prev_num) if posts.prev_num else None
    return render_template('gallery/home.html.j2', title='Gallery', posts=posts, next_url=next_url, prev_url=prev_url)


@flask_app.route('/gallery/create', methods=['GET', 'POST'])
@login_required
def gallery_create_post():
    form = forms.CreateGallery()
    if form.validate_on_submit():
        gallery_category = models.GalleryCategory.query.filter_by(name = form.category.data or 'others').first()
        if not gallery_category:
            gallery_category = models.GalleryCategory(name = form.category.data or 'others')
        gallery_post = models.GalleryPost(
            title = form.title.data,
            description = form.description.data,
            author = current_user,
            category = gallery_category)
        for image in request.files.getlist('images'):
            gallery_post_image = models.GalleryPostImage(
                path = google_cloud.upload_blob_to_bucket(
                    bucket_name=flask_app.config['GOOGLE_STORAGE_BUCKET'],
                    object_key=f"images/{md5(f'gallery{gallery_post.title}_{current_user.username}_{image.filename}'.encode('utf-8')).hexdigest()}",
                    content=image.read(),
                    content_type='image/jpeg'
                ), post = gallery_post)
        db.session.add_all([gallery_category, gallery_post, gallery_post_image])
        db.session.commit()
        flash('Thank you for your submission', 'success')
        return redirect(url_for('gallery'))
    return render_template('gallery/create.html.j2', form=form)


@flask_app.route('/gallery/p/<int:post_id>')
def gallery_post_view(post_id: int):
    post = models.GalleryPost.query.filter_by(id = post_id).first_or_404()
    post.add_view_count()
    return render_template('gallery/view.html.j2', post=post)


@flask_app.route('/secondhand/p')
@flask_app.route('/secondhand')
def secondhand():
    page = request.args.get("page", 1, type=int)
    posts = models.SecondHandPost.query.order_by(models.SecondHandPost.issue_date.desc()).paginate(page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for('secondhand', page=posts.next_num) if posts.next_num else None
    prev_url = url_for('secondhand', page=posts.prev_num) if posts.prev_num else None
    return render_template('secondhand/home.html.j2', title='Second Hand Market', posts=posts, next_url=next_url, prev_url=prev_url)


@flask_app.route('/secondhand/create', methods=['GET', 'POST'])
@login_required
def secondhand_create_post():
    form = forms.CreateSecondHandPost()
    if form.validate_on_submit():
        secondhand_post = models.SecondHandPost(
            title = form.title.data,
            description = form.description.data,
            seller = current_user)
        for image in request.files.getlist('images'):
            secondhand_post_image = models.SecondHandImage(
                path = google_cloud.upload_blob_to_bucket(
                    bucket_name=flask_app.config['GOOGLE_STORAGE_BUCKET'],
                    object_key=f"images/{md5(f'gallery{secondhand_post.title}_{current_user.username}_{image.filename}'.encode('utf-8')).hexdigest()}",
                    content=image.read(),
                    content_type='image/jpeg'),
                post = secondhand_post)
        db.session.add_all([secondhand_post, secondhand_post_image])
        db.session.commit()
        flash('Thank you for your submission')
        return redirect(url_for('secondhand'))
    return render_template('secondhand/create.html.j2', form=form)


@flask_app.route('/secondhand/p/<int:post_id>')
def secondhand_post_view(post_id: int):
    post = models.SecondHandPost.query.filter_by(id = post_id).first_or_404()
    post.add_view_count()
    return render_template('secondhand/view.html.j2', post=post)
