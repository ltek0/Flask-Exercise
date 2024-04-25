from functools import wraps
from flask import render_template, request, url_for, abort, redirect
from flask_login import current_user
from flask_babel import gettext, _
from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    DateTimeField,
    ValidationError,
    TextAreaField,
    MultipleFileField,
    EmailField
)

from wtforms.validators import (
    DataRequired, 
    Length, 
    Email, 
    EqualTo, 
    Optional
)

from . import flask_app, models, db
import re



###################################################################################
# Froms
def _username_validator(curr_username: str = None, username: str = None):
    if not re.fullmatch(r'\b[A-Za-z0-9._]{3,32}\b', username):
        raise ValidationError(gettext('Username must be between 3 and 24 characters long and contain only letters, numbers, dots and underscores.'))
    if curr_username != username and models.User.query.filter_by(username=username).first():
        raise ValidationError(gettext("Username not avaliable. Please use a different username."))

class CreateUser(FlaskForm):
    display_name = StringField(gettext('Display Name'), validators=[Length(max=100, message='Max Allowed leanth is 100 Charactor')])
    username = StringField(gettext("Username"), validators=[DataRequired(), Length(max=64, message='Max Allowed leanth is 64 Charactor')])
    email = EmailField(gettext("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(gettext("Password"), validators=[DataRequired()])
    role = StringField(gettext('Role'), validators=[Optional(), Length(max=64, message='Max Allowed leanth is 64 Charactor')])
    about_me = TextAreaField(gettext('About Me'), validators=[Optional(), Length(max=256, message='Max Allowed leanth is 256 Charactor')])
    submit = SubmitField(gettext("Create"))
    def validate_username(self, username: StringField):
        _username_validator(username=username.data)
    def validate_email(self, email: StringField):
        if models.User.query.filter_by(username=email.data).first():
            raise ValidationError(gettext("This email is already in use."))

class EditUser(FlaskForm):
    username = StringField(gettext('Username'))
    display_name = StringField(gettext('Display Name'), validators=[Length(max=100, message='Max Allowed leanth is 100 Charactor')])
    about_me = TextAreaField(gettext('About Me'), validators=[Length(max=256, message='Max Allowed leanth is 256 Charactor')])
    email = EmailField(gettext('Email'), validators=[Email()])
    role = StringField(gettext('Role'), validators=[Length(max=64, message='Max Allowed leanth is 64 Charactor')])
    submit = SubmitField(gettext('Save Changes'))
    def __init__(self, original_username, *args, **kwargs):
        super(EditUser, self).__init__(*args, **kwargs)
        self.original_username = original_username
    def validate_username(self, username: StringField):
        _username_validator(
            curr_username=self.original_username, username=username.data)
    def validate_email(self, email: StringField):
        if models.User.query.filter_by(username=email.data).first():
            raise ValidationError(gettext("This email is already in use."))


class DeleteUser(FlaskForm):
    confirm = StringField(gettext('Please input the users username to delete'), validators=[DataRequired(message="Please input the user's username to delete the user")])
    submit = SubmitField(gettext("Delete User"))
    def __init__(self, original_username, *args, **kwargs):
        super(DeleteUser, self).__init__(*args, **kwargs)
        self.original_username = original_username
    def validate_confirm(self, confirm: StringField):
        if confirm.data != self.original_username:
            raise ValidationError(gettext("Please input the user's username to delete the user"))


###################################################################################
# Routes
@flask_app.route('/admin')
def admin():
    return render_template('admin/index.html.j2', title='Admin')


@flask_app.route('/admin/user')
def admin_user():
    page = request.args.get("page", 1, type=int)
    users = models.User.query.paginate(
        page=page, per_page=10, error_out=False)
    next_url = url_for(
        'admin_user', page=users.next_num) if users.next_num else None
    prev_url = url_for(
        'admin_user', page=users.prev_num) if users.prev_num else None
    return render_template('admin/users.html.j2', title='User Administration', users=users, next_url=next_url, prev_url=prev_url)


@flask_app.route('/admin/user/<username>/edit', methods=['GET', 'POST'])
def admin_user_edit(username: str):
    user = models.User.query.filter_by(username=username).first_or_404()
    form = EditUser(user.username)
    if form.validate_on_submit():
        user.username = form.username.data
        user.display_name = form.display_name.data
        user.email = form.email.data
        user.role_name = form.role.data
        user.about_me = form.about_me.data
        db.session.commit()
        return redirect(url_for('admin_user'))
    elif request.method == 'GET':
        form.username.data = user.username
        form.display_name.data = user.display_name
        form.email.data = user.email
        form.role.data = user.role.name
        form.about_me.data = user.about_me
    return render_template('admin/user_edit.html.j2', title='Edit User', form=form, user=user)


@flask_app.route('/admin/user/<username>/delete', methods=['GET', 'POST'])
def admin_user_delete(username: str):
    user = models.User.query.filter_by(username=username).first_or_404()
    form = DeleteUser(user.username)
    if form.validate_on_submit():
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('admin_user'))
    return render_template('admin/user_delete.html.j2', title='Delete User', form=form, user=user)


@flask_app.route('/admin/create_user', methods=['GET', 'POST'])
def admin_user_create():
    form = CreateUser()
    if form.validate_on_submit():
        user = models.User(
            username=form.username.data,
            display_name=form.display_name.data,
            about_me=form.about_me.data,
            email=form.email.data,
            role_name=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('admin_user'))
    return render_template('admin/user_create.html.j2', title='Create User', form=form)