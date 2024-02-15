from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email , ValidationError, EqualTo

import sqlalchemy as sa

from app import db
from app.models import User

import re

class user():
    class Login(FlaskForm):
        username = StringField('Username', validators=[DataRequired()])
        password = PasswordField('Password', validators=[DataRequired()])
        remember_me = BooleanField('Remember Me')
        submit = SubmitField('Sign In')

    class Register(FlaskForm):
        username = StringField('Username', validators=[DataRequired()])
        email = StringField('Email', validators=[DataRequired(), Email()])
        password = PasswordField('Password', validators=[DataRequired()])
        password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
        submit = SubmitField('Register')

        def validate_username(self, username: str):
            if not re.fullmatch(r'\b[A-Za-z0-9._]{3,24}\b', username.data):
                raise ValidationError('Username must be between 3 and 24 characters long and contain only letters, numbers, dots and underscores.')
            if db.session.scalar(sa.select(User).where(User.username == username.data)):
                raise ValidationError('Username not avalable. Please use a different username.')

        def validate_email(self, email: str ):
            if db.session.scalar(sa.select(User).where(User.email == email.data)):
                raise ValidationError('An account with this email already exist. Please use a different email.')
        
        def validate_password(self, password: str):
            conditions = ['Your password must:']
            if len(password.data) < 8:
                conditions.append('be at least 8 characters long.')
            if not re.search('[a-z]', password.data):
                conditions.append('contain at least one lowercase letter.')
            if not re.search('[A-Z]', password.data):
                conditions.append('contain at least one uppercase letter.')
            if not re.search('[0-9]', password.data):
                conditions.append('contain at least one number.')
            if len(conditions) > 1:
                raise ValidationError('\n'.join(conditions))