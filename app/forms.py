from collections.abc import Sequence
from flask_wtf import FlaskForm
from flask_babel import gettext

from wtforms import StringField, IntegerField, PasswordField, BooleanField, SubmitField, ValidationError, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_wtf.file import FileRequired,  FileAllowed

from .models import User

import re


def _username_validator(curr_username:str = None, username: str= None):
    if not re.fullmatch(r'\b[A-Za-z0-9._]{3,32}\b', username):
        raise ValidationError(gettext('Username must be between 3 and 24 characters long and contain only letters, numbers, dots and underscores.'))
    if curr_username != username:
        if User.query.filter_by(username=username).first():
            raise ValidationError(gettext("Username not avaliable. Please use a different username."))


def _password_validator(password: str):
    conditions = ['Your password must:']
    if len(password) < 8:
        conditions.append('contain at least one lowercase letter.')
    if not re.search('[A-Z]', password):
        conditions.append('contain at least one uppercase letter.')
    if not re.search('[0-9]', password):
        conditions.append('contain at least one number.')
    if len(conditions) > 1:
        raise ValidationError(''.join(conditions))


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

    def validate_username(self, username: StringField):
        _username_validator(username=username.data)
    
    def validate_email(self, email: StringField):
        if User.query.filter_by(username=email.data).first():
            raise ValidationError(gettext("This email is already in use."))

    def validate_password(self, password: StringField):
        _password_validator(password=password.data)


class EditProfileForm(FlaskForm):
    username = StringField(gettext('Username'))
    display_name = StringField(gettext('Display Name'), validators=[Length(max=100, message='Max Allowed leanth is 100 Charactor')])
    about_me = TextAreaField(gettext('About Me'), validators=[Length(max=256, message='Max Allowed leanth is 256 Charactor')])
    submit = SubmitField(gettext('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username: StringField):
        _username_validator(curr_username=self.original_username, username=username.data)
    

class CreatePostForm(FlaskForm):
    title = StringField(gettext('Title'), validators=[Length(min=0, max=128)])
    body = TextAreaField(gettext('Say something to the world'), validators=[DataRequired(), Length(min=0, max=512)])
    submit = SubmitField(gettext('Post'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(gettext("Email"), validators=[DataRequired(), Email()])
    submit = SubmitField(gettext("Request Password Reset"))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(gettext("New password"), validators=[DataRequired()])
    password2 = PasswordField(gettext("Repeat new Password"), validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField(gettext("Reset password"))

    def validate_password(self, password: StringField):
        _password_validator(password=password.data)


class CreateGallery(FlaskForm):
    title = StringField(gettext('Title'), validators=[DataRequired(message='A title for your submission is required'), Length(max=128, min=1, message='Title must be less then 128 charactor')])
    images = MultipleFileField(gettext('Select Photos'), validators=[FileRequired(message="You must provide at least one image"), FileAllowed(['jpg', 'png', 'gif'], message='You can only upload images!')])
    description = TextAreaField(gettext("Description"), validators=[Length(max=512, min=0, message='Description must be less then 512 charactor')])
    submit = SubmitField("Upload")

    def validate_images(self, images: MultipleFileField):
        if len(images.data) > 10:
            raise ValidationError('You can upload a maximum of 10 images')
        

class CreateSecondHandPost(FlaskForm):
    title = StringField(gettext('Title'), validators=[DataRequired(message='A title for your submission is required'), Length(max=128, min=1, message='Title must be less then 128 charactor')])
    type = StringField(gettext('Type'), validators=[DataRequired(message='Type of product is required')])
    price = IntegerField(gettext('Price'), default=0, validators=[DataRequired(message='Type of product is required')])
    images = MultipleFileField(gettext('Select Photos'), validators=[FileAllowed(['jpg', 'png', 'gif'], message='You can only upload images!')])
    description = TextAreaField(gettext("Description"), validators=[Length(max=512, min=0, message='Description must be less then 512 charactor')])
    submit = SubmitField("Submit")

    def validate_images(self, images: MultipleFileField):
        if len(images.data) > 10:
            raise ValidationError('You can upload a maximum of 10 images')