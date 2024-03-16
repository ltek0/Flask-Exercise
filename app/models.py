import werkzeug.security
from datetime import datetime as dt, UTC, timedelta as td
from typing import Self
import jwt
from hashlib import md5

from flask_login import UserMixin

from . import db, login_manager, flask_app


followers = db.Table(
    'Followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False, index=True, unique=True)
    email = db.Column(db.String(128), nullable=False, index=True, unique=True)
    _passowrd_hash = db.Column(db.String(256), nullable=False, index=True)
    _last_seen = db.Column(db.DateTime, nullable=True)
    _display_name = db.Column(db.String(100), nullable=True) 
    _about_me = db.Column(db.String(256), nullable=True)
    posts = db.relationship('Post', backref='author', lazy='select')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __init__(self, 
                 username:str,
                 email:str, 
                 display_name:str = None,
                 about_me:str=None):
        self.username = username
        self.email = email
        self._display_name = display_name or self.username
        self._about_me = about_me or 'creator'

    def __repr__(self) -> str:
        return f'<User {self.id}:{self.username}>'
    
    @property
    def last_seen(self):
        return self._last_seen or 'User have not loggin yet.'

    def update_last_seen(self):
        self._last_seen = dt.now(UTC)
        db.session.commit()

    @property
    def display_name(self) -> str:
        return self._display_name
    
    @display_name.setter
    def display_name(self, new_display_name: str) -> None:
        if not new_display_name:
            self._display_name = None
        elif len(new_display_name) <= 100:
            self._display_name = new_display_name
        else:
            raise ValueError('Display name is too long.')
    
    @property
    def about_me(self):
        return self._about_me or ''
    
    @about_me.setter
    def about_me(self, new_about_me: str):
        if not new_about_me:
            self._about_me = None
        elif len(new_about_me) <= 256:
            self._about_me = new_about_me
        else:
            raise ValueError('About me is too long.')

    def set_password(self, password: str) -> None:
        self._passowrd_hash = werkzeug.security.generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return werkzeug.security.check_password_hash(self._passowrd_hash, password)

    def create(self): # returns the full user object on sucess and None on error
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as ex:
            db.session.rollback()
            flask_app.logger.error(ex)
            return None

    def avatar(self, size: int) -> str:
        email_md5 = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{email_md5}?d=identicon&s={size}'

    def is_following(self, user: Self):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def follow(self, user: Self): # returns True on sucess and false on error
        try:
            if not self.is_following(user):
                self.followed.append(user)
                db.session.commit()
                return True
            return False
        except Exception as ex:
            db.session.rollback()
            flask_app.logger.error(ex)
            return False

    def unfollow(self, user: Self): # returns True on sucess and false on error
        try:
            if self.is_following(user):
                self.followed.remove(user)
                db.session.commit()
                return True
            return False
        except Exception as ex:
            db.session.rollback()
            flask_app.logger.error(ex)
            return False

    @property
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id = self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in: int = 600):
        return jwt.encode({"reset_password": self.id,
                           "exp": dt.now(UTC) + td(seconds=expires_in)},
                          flask_app.config["SECRET_KEY"], algorithm="HS256")
        
    @staticmethod
    def verify_reset_password_token(token: str):
        try:
            id = jwt.decode(token, flask_app.config["SECRET_KEY"], algorithms="HS256")["reset_password"]
        except Exception as ex:
            flask_app.logger.error('Invalid tokin used')
            flask_app.logger.error(ex)
            return None
        return User.query.get(id)


@login_manager.user_loader
def load_user(id: int):
    return User.query.get(int(id))

 
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _title = db.Column(db.String(128))
    body = db.Column(db.String(512))
    timestamp = db.Column(db.DateTime, default=lambda: dt.now(UTC))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def title(self) -> str:
        return self._title or ""
    
    @title.setter
    def title(self, title: str) -> None:
        if not title:
            self._title = None
        elif len(title) <= 128:
            self._title = title
        else:
            raise ValueError('Title is too long')

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as ex:
            db.session.rollback()
            flask_app.logger.error(ex)
            return None
    
    def __repr__(self) -> str:
        return f"<Post '{self.id}:{self.body}'>"