from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email , ValidationError, EqualTo, Length

import sqlalchemy as sa

from app import db
from app.models import User

import re


class user():
    class Login(FlaskForm):
        username = StringField('Username or Email', validators=[DataRequired(), Length(min = 0, max = 64)])
        password = PasswordField('Password', validators=[DataRequired()])
        remember_me = BooleanField('Remember Me')
        submit = SubmitField('Sign In')


    class Register(FlaskForm):
        username = StringField('Username', validators=[DataRequired(), Length(min = 3, max = 32)])
        display_name = StringField('Display Name (Optional)', validators=[Length(min = 0, max = 24)])
        bio = StringField('Bio (optinoal)', validators=[Length(min = 0, max = 64)])
        email = StringField('Email', validators=[DataRequired(), Email()])
        password = PasswordField('Password', validators=[DataRequired()])
        password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
        submit = SubmitField('Register')

        # check if username only contains the following
        # A-Z, a-Z, 0-9, '.', '_'
        # between 3 to 32 charactor
        # is not a used username
        def validate_username(self, username: str):
            if not re.fullmatch(r'\b[A-Za-z0-9._]{3,32}\b', username.data):
                raise ValidationError('Username must be between 3 and 24 characters long and contain only letters, numbers, dots and underscores.')
            if db.session.scalar(sa.select(User).where(User.username == username.data)):
                raise ValidationError('Username not avalable. Please use a different username.')

        # check for existing user with the same email
        def validate_email(self, email: str ):
            if db.session.scalar(sa.select(User).where(User.email == email.data)):
                raise ValidationError('An account with this email already exist. Please use a different email.')

        # password contains the following
        # at least 8 char, A-z + number
        def validate_password(self, password: str):
            conditions = ['Your password must:']
            if len(password.data) < 8:
                conditions.append('be at least 8 characters long.')
            if not re.search('[a-z]', password.data):
                conditions.append('contain at least one lowercase letter.')
            if not re.search('[A-Z]', password.data):
                conditions.append('contain at least one uppercase letter.')
            if not re.search('[0-9]', password.data) or len(password.data) <= 1:
                conditions.append('contain at least one number.')
            if len(conditions) > 1:
                raise ValidationError('\n'.join(conditions))


    class EditProfile(FlaskForm):
        display_name = StringField('Display Name (Optional)', validators=[Length(min = 0, max = 24)])
        bio = StringField('Bio (optinoal)', validators=[Length(min = 0, max = 64)])
        submit = SubmitField('Submit')

class post:
    class Create(FlaskForm):
        body = StringField('Say something', validators=[DataRequired(), Length(min = 1, max = 140)])
        title = StringField('Title', validators=[DataRequired(), Length(min = 1, max = 64)])
        submit = SubmitField('Create')

    class Edit(FlaskForm):
        body = StringField('Edit Your Post', validators=[DataRequired(), Length(min = 1, max = 140)])
        submit = SubmitField('Submit')


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')