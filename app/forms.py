from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from flask_babel import gettext

from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from .models import User

import re

class LoginForm(FlaskForm):
    username = StringField(gettext("Username or email"), validators=[DataRequired()])
    password = PasswordField(gettext("Password"), validators=[DataRequired()])
    remember_me = BooleanField(gettext("Remember Me"))
    submit = SubmitField(gettext("Sign In"))


class RegisterForm(FlaskForm):
    display_name = StringField(gettext('Display Name'), validators=[Length(max=100, message='Max Allowed leanth is 100 Charactor')])
    username = StringField(gettext("Username"), validators=[DataRequired(), Length(max=64, message='Max Allowed leanth is 64 Charactor')])
    email = StringField(gettext("Email"), validators=[DataRequired(), Email()])
    password = PasswordField(gettext("Password"), validators=[DataRequired()])
    password2 = PasswordField(gettext("Repeat Password"), validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField(gettext("Register"))

    def validate_username(self, username: str):
        if not re.fullmatch(r'\b[A-Za-z0-9._]{3,32}\b', username.data):
            raise ValidationError(gettext('Username must be between 3 and 24 characters long and contain only letters, numbers, dots and underscores.'))
        if User.query.filter_by(username=username.data).first():
            raise ValidationError(gettext("Username not avaliable. Please use a different username."))
    
    def validate_email(self, email: str):
        if User.query.filter_by(username=email.data).first():
            raise ValidationError(gettext("This email is already in use."))


class EditProfileForm(FlaskForm):
    username = StringField(gettext('Username'))
    display_name = StringField(gettext('Display Name'), validators=[Length(max=100, message='Max Allowed leanth is 100 Charactor')])
    about_me = TextAreaField(gettext('About Me'), validators=[Length(max=256, message='Max Allowed leanth is 256 Charactor')])
    submit = SubmitField(gettext('Submit'))

    def __init_gettext(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init_gettext(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if not re.fullmatch(r'\b[A-Za-z0-9._]{3,32}\b', username.data):
            raise ValidationError('Username must be between 3 and 24 characters long and contain only letters, numbers, dots and underscores.')
        if username.data != self.original_username:
            if User.query.filter_by(username=username.data).first():
                raise ValidationError(gettext("Username not avaliable. Please use a different username."))
    

class CreatePostForm(FlaskForm):
    title = StringField(gettext('Title'), validators=[Length(min=0, max=128)])
    body = TextAreaField(gettext('Say something to the world'), validators=[DataRequired(), Length(min=0, max=512)])
    submit = SubmitField(gettext('Submit'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(gettext("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(gettext("Request Password Reset"))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(gettext("New password"), validators=[DataRequired()])
    password2 = PasswordField(gettext("Repeat new Password"), validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField(gettext("Reset password"))