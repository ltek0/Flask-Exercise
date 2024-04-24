from functools import wraps
from flask import render_template, request, url_for, abort
from flask_login import current_user
from flask_babel import _

from . import flask_app, models


@flask_app.route('/admin')
def admin():
    return render_template('admin/index.html.j2', title='Admin')


# ------------------------  user managment ------------------------
@flask_app.route('/admin/user')
def admin_user():
    page = request.args.get("page", 1, type=int)
    users = models.User.query.paginate(
        page=page, per_page=10, error_out=False)
    next_url = url_for(
        'admin_user', page=users.next_num) if users.next_num else None
    prev_url = url_for(
        'admin_user', page=users.prev_num) if users.prev_num else None
    return render_template('admin/user.html.j2', title='User Administration', users=users, next_url=next_url, prev_url=prev_url)


@flask_app.route('/admin/user/<username>')
def admin_user_view(username: str):
    user = models.User.query.filter_by(username=username).first_or_404()
    return render_template('admin/user_view.html.j2', title='User Profile', user=user)


@flask_app.route('/admin/user/<username>/edit')
def admin_user_edit(username: str):
    return "Page for editing User"


@flask_app.route('/admin/user/<username>/delete')
def admin_user_delete(username: str):
    return "delete user confremation"


@flask_app.route('/admin/create_user')
def admin_user_create():
    return "page for creating user"


# ------------------------  post managment ------------------------
@flask_app.route('/admin/role')
def admin_role():
    return 'page for role managment'


@flask_app.route('/admin/role/<role_name>')
def admin_role_view(role_name: str):
    return 'page for role managment'


@flask_app.route('/admin/create_role')
def admin_role_create():
    return 'page for role managment'


# ------------------------  gallery managment ------------------------
@flask_app.route('/admin/gallery')
def admin_gallery():
    return 'page for gallery managment'


# ------------------------  secondhand post managment ------------------------
@flask_app.route('/admin/secondhand')
def admin_secondhand():
    return 'page for secondhand post managment'
