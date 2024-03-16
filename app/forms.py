from collections.abc import Sequence
from typing import Any, Mapping
from flask_wtf import FlaskForm
from flask_wtf.form import _Auto
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo

from .models import User

import re

class LoginForm(FlaskForm):
    username = StringField("Username or email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegisterForm(FlaskForm):
    display_name = StringField('Display Name', validators=[Length(max=100, message='Max Allowed leanth is 100 Charactor')])
    username = StringField("Username", validators=[DataRequired(), Length(max=64, message='Max Allowed leanth is 64 Charactor')])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField("Repeat Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

    def validate_username(self, username: str):
        if not re.fullmatch(r'\b[A-Za-z0-9._]{3,32}\b', username.data):
            raise ValidationError('Username must be between 3 and 24 characters long and contain only letters, numbers, dots and underscores.')
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Username not avaliable. Please use a different username.")
    
    def validate_email(self, email: str):
        if User.query.filter_by(username=email.data).first():
            raise ValidationError("This email is already in use.")


class EditProfileForm(FlaskForm):
    username = StringField('Username')
    display_name = StringField('Display Name', validators=[Length(max=100, message='Max Allowed leanth is 100 Charactor')])
    about_me = TextAreaField('About Me', validators=[Length(max=256, message='Max Allowed leanth is 256 Charactor')])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if not re.fullmatch(r'\b[A-Za-z0-9._]{3,32}\b', username.data):
            raise ValidationError('Username must be between 3 and 24 characters long and contain only letters, numbers, dots and underscores.')
        if username.data != self.original_username:
            if User.query.filter_by(username=username.data).first():
                raise ValidationError("Username not avaliable. Please use a different username.")
    

class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[Length(min=0, max=128)])
    body = TextAreaField('Say something to the world', validators=[DataRequired(), Length(min=0, max=512)])
    submit = SubmitField('Submit')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Password Reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("New password", validators=[DataRequired()])
    password2 = PasswordField("Repeat new Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Reset password")