from flask import render_template, flash, redirect, url_for, request, abort, g
from flask_login import login_user, current_user, login_required, logout_user
from flask_babel import _, get_locale

from werkzeug.utils import secure_filename
from urllib.parse import urlparse
from datetime import datetime as dt, UTC
from hashlib import sha256, md5
from threading import Thread

from . import flask_app, db, forms
from .models import User, Post, PasswordResetTokens
from .email import send_password_reset_email

import app.models as models
import app.google_cloud as google_cloud


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
            title=form.title.data,
            body=form.body.data,
            author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is live'))
        # after form submit, redirect, otherwise, form data will not be cleared
        return redirect(url_for('index'))
    page = request.args.get("page", 1, type=int)
    posts = current_user.followed_posts().paginate(
        page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'index', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'index', page=posts.prev_num) if posts.prev_num else None
    return render_template("index.html.j2", title="Home", form=form, posts=posts.items, next_url=next_url, prev_url=prev_url, home=True)


@flask_app.route('/explore')
def explore():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'explore', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'explore', page=posts.prev_num) if posts.prev_num else None
    return render_template("index.html.j2", title="Explore", posts=posts.items, next_url=next_url, prev_url=prev_url)


@flask_app.route('/explore/<int:post_id>')
def explore_post(post_id: int):
    # TODO: create page for posts to allow comments
    pass


@flask_app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(db.or_(
            User.email == form.username.data, User.username == form.username.data)).first()
        if user is not None and user.check_password(form.password.data) is True:
            login_user(user, remember=form.remember_me.data)
            flash(_('Welcome Back!'))
            return redirect(url_for('index'))
        flash(_('Invalid username or password'))
        return redirect(url_for('login'))
    return render_template('user/login.html.j2', title="Sign In", form=form)


@flask_app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.RegisterForm()
    if form.validate_on_submit():
        u = User(username=form.username.data,
                 email=form.email.data,
                 display_name=form.display_name.data)
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
    posts = Post.query.filter_by(author=user).order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for('profile', page=posts.next_num,
                       username=username) if posts.next_num else None
    prev_url = url_for('profile', page=posts.prev_num,
                       username=username) if posts.prev_num else None
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
    # TODO: change password
    pass


@flask_app.route("/reset_password", methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = forms.ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            _('An email will be sent to you shortly if the email is found in our records'))
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
    current_user_profile = redirect(
        url_for('profile', username=current_user.username))
    user = User.query.filter_by(username=username).first()
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
    current_user_profile = redirect(
        url_for('profile', username=current_user.username))
    user = User.query.filter_by(username=username).first()
    if not user:
        flash(_('user %(n)s was not found', n=username))
        return current_user_profile
    if user == current_user:
        flash(_('You cannot unfollow yourself'))
        return current_user_profile
    current_user.unfollow(user)
    flash(_('You are no longer following %(a)s', a=user.display_name))
    return redirect(url_for('profile', username=user.username))


@flask_app.route('/gallery/post')
@flask_app.route('/gallery/post/')
@flask_app.route('/gallery')
@flask_app.route('/gallery/')
def gallery():
    page = request.args.get("page", 1, type=int)
    posts = models.GalleryPost.query.order_by(models.GalleryPost.timestamp.desc()).paginate(
        page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'gallery', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'gallery', page=posts.prev_num) if posts.prev_num else None
    return render_template('gallery/home.html.j2', title='Gallery', posts=posts, next_url=next_url, prev_url=prev_url)


@flask_app.route('/gallery/category')
@flask_app.route('/gallery/category/')
def gallery_category():
    page = request.args.get("page", 1, type=int)
    categories = models.GalleryCategory.query.paginate(
        page=page, per_page=20, error_out=False)
    next_url = url_for(
        'gallery_category', page=categories.next_num) if categories.next_num else None
    prev_url = url_for(
        'gallery_category', page=categories.prev_num) if categories.prev_num else None
    return render_template('gallery/category_list.html.j2', title='Gallery', categories=categories, next_url=next_url, prev_url=prev_url)


@flask_app.route('/gallery/category/<category>')
@flask_app.route('/gallery/category/<category>/')
def gallery_category_view(category: str):
    category = models.GalleryCategory.query.filter_by(
        name=category).first_or_404()
    page = request.args.get("page", 1, type=int)
    posts = models.GalleryPost.query.filter_by(category=category).order_by(models.GalleryPost.timestamp.desc()).paginate(
        page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'gallery_category_view', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'gallery_category_view', page=posts.prev_num) if posts.prev_num else None
    return render_template('gallery/category_view.html.j2', title='Gallery', posts=posts, next_url=next_url, prev_url=prev_url, category=category)


def upload_store_image(post, image, current_user):
    object_key = f"{md5(f'{post.title}{current_user.username}{secure_filename(image.filename)}{dt.now(UTC)}'.encode('utf-8')).hexdigest()}"
    post_image = models.GalleryPostImage(object_key=object_key, post=post)
    Thread(target=google_cloud.upload_blob_to_bucket,
           kwargs={
               'object_key': object_key,
               'content': image.read(),
               'content_type': 'image/jpeg'}).start()
    db.session.add(post_image)


@flask_app.route('/gallery/create', methods=['GET', 'POST'])
@login_required
def create_gallery():
    form = forms.CreateGallery()
    if form.validate_on_submit():
        post = models.GalleryPost(
            title=form.title.data,
            description=form.description.data,
            author=current_user,
            category=form.category.data or 'General')
        db.session.add(post)
        for image in request.files.getlist('images'):
            upload_store_image(post, image, current_user)
        db.session.commit()
        flash('Thank you for your submission')
        return redirect(url_for('gallery'))
    return render_template('gallery/create.html.j2', form=form)


@flask_app.route('/gallery/post/<int:post_id>')
def view_gallery(post_id: int):
    post = models.GalleryPost.query.filter_by(id=post_id).first_or_404()
    post.view()
    return render_template('gallery/view.html.j2', post=post, IMGC=len(post.images))


@flask_app.route('/gallery/post/<int:post_id>/edit', methods=["GET", "POST"])
def edit_gallery(post_id: int):
    post = models.GalleryPost.query.filter_by(id=post_id).first_or_404()
    if post.author != current_user:
        flash('You can only edit your own post!')
        return redirect(url_for('view_gallery', post_id=post_id))
    edit_post = forms.EditGallery()
    if edit_post.validate_on_submit():
        post.title = edit_post.title.data
        post.description = edit_post.description.data
        post.category.name = edit_post.category.data
        db.session.commit()
        return redirect(url_for('view_gallery', post_id=post.id))
    edit_post.title.data = post.title
    edit_post.description.data = post.description
    edit_post.category.data = post.category.name
    return render_template('gallery/edit.html.j2', form=edit_post, post=post)


@flask_app.route('/gallery/post/<int:post_id>/add_images', methods=["GET", "POST"])
def add_gallery_image(post_id: int):
    post = models.GalleryPost.query.filter_by(id=post_id).first_or_404()
    if post.author != current_user:
        flash('You can only edit your own post!')
        return redirect(url_for('view_gallery', post_id=post_id))
    add_image = forms.AddGalleryImages()
    if add_image.validate_on_submit():
        existing_image_count = models.GalleryPostImage.query.filter_by(
            gallerypost_id=post.id).count()
        if existing_image_count + len(request.files.getlist('images')) > flask_app.config['IMAGE_PER_GALLERY']:
            flash(f'You can only have {flask_app.config["IMAGE_PER_GALLERY"]} images in a post!')
            return redirect(url_for('view_gallery', post_id=post.id))
        for image in request.files.getlist('images'):
            upload_store_image(post, image, current_user)
        db.session.commit()
        return redirect(url_for('view_gallery', post_id=post.id))
    return render_template('gallery/add_image.html.j2', form=add_image, post=post)


@flask_app.route('/gallery/post/<int:post_id>/delete_images', methods=["GET", "POST"])
def delete_gallery_image(post_id: int):
    post = models.GalleryPost.query.filter_by(id=post_id).first_or_404()
    if post.author != current_user:
        flash('You can only edit your own post!')
        return redirect(url_for('view_gallery', post_id=post_id))
    delete_image = forms.DeleteGalleryImages(post_id=post.id)
    if delete_image.validate_on_submit():
        # TODO: better implimentation
        image = models.GalleryPostImage.query.filter_by(
            object_key=delete_image.filehash.data, gallerypost_id=post.id).first()
        if image:
            Thread(target=google_cloud.delete_from_object_key,
                   kwargs={'object_key': image.object_key})
            db.session.delete(image)
            db.session.commit()
            flash(f'deleted {delete_image.filehash.data}')
        else:
            flash('Image was not found')
        return redirect(url_for('view_gallery', post_id=post.id))
    return render_template('gallery/delete_image.html.j2', form=delete_image, post=post, title='Delete Image')


@flask_app.route('/secondhand/p')
@flask_app.route('/secondhand')
def secondhand():
    page = request.args.get("page", 1, type=int)
    posts = models.SecondHandPost.query.order_by(models.SecondHandPost.issue_date.desc(
    )).paginate(page=page, per_page=flask_app.config["POSTS_PER_PAGE"], error_out=False)
    next_url = url_for(
        'secondhand', page=posts.next_num) if posts.next_num else None
    prev_url = url_for(
        'secondhand', page=posts.prev_num) if posts.prev_num else None
    return render_template('secondhand/home.html.j2', title='Second Hand Market', posts=posts, next_url=next_url, prev_url=prev_url)


@flask_app.route('/secondhand/create', methods=['GET', 'POST'])
@login_required
def secondhand_create_post():
    form = forms.CreateSecondHandPost()
    if form.validate_on_submit():
        secondhand_post = models.SecondHandPost(
            title=form.title.data,
            type=form.type.data,
            price=form.price.data,
            publish_until=form.publish_until.data,
            description=form.description.data,
            seller=current_user)
        for image in request.files.getlist('images'):
            secondhand_post_image = models.SecondHandImage(
                object_key=google_cloud.upload_blob_to_bucket(
                    bucket_name=flask_app.config['GOOGLE_STORAGE_BUCKET'],
                    object_key=f"images/{md5(f'gallery{secondhand_post.title}_{current_user.username}_{image.filename}'.encode('utf-8')).hexdigest()}",
                    content=image.read(),
                    content_type='image/jpeg'),
                post=secondhand_post)
        db.session.add_all([secondhand_post, secondhand_post_image])
        db.session.commit()
        flash('Thank you for your submission')
        return redirect(url_for('secondhand'))
    return render_template('secondhand/create.html.j2', form=form)


@flask_app.route('/secondhand/p/<int:post_id>')
def secondhand_post_view(post_id: int):
    post = models.SecondHandPost.query.filter_by(id=post_id).first_or_404()
    post.add_view_count()
    return render_template('secondhand/view.html.j2', post=post)


#------------------------------------------------------------------------------
@flask_app.route('/news')
def news():
    return render_template('others/news.html.j2', title=_('News'))


@flask_app.route('/cameras')
def cameras():
    return render_template('others/cameras.html.j2', title=_('Cameras'))


@flask_app.route('/phones')
def phones():
    return render_template('others/phones.html.j2', title=_('Phones'))


@flask_app.route('/cars')
def cars():
    return render_template('others/cars.html.j2', title=_('Cars'))


@flask_app.route('/shop')
def shop():
    return render_template('others/shop.html.j2', title=_('Shop'))


@flask_app.route('/photography')
def photography():
    return render_template('others/photography.html.j2', title=_('Photography'))


@flask_app.route('/travel')
def travel():
    return render_template('others/travel.html.j2', title=_('Travel'))

#------------------------------------------------------------------------------