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
    _password_hash = db.Column(db.String(256), nullable=False, index=True)
    last_seen = db.Column(db.DateTime, nullable=True)
    display_name = db.Column(db.String(100), nullable=True) 
    about_me = db.Column(db.String(256), nullable=True)
    posts = db.relationship('Post', backref='author', lazy='select')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __init__(self, username:str, email:str, display_name:str = None, about_me:str = None):
        self.username = username
        self.email = email
        self.display_name = display_name or self.username
        self._about_me = about_me or '---'

    def __repr__(self) -> str:
        return f'<User {self.id}:{self.username}>'

    def set_password(self, password: str) -> None:
        self._password_hash = werkzeug.security.generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return werkzeug.security.check_password_hash(self._password_hash, password)

    def avatar(self, size: int) -> str:
        email_md5 = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{email_md5}?d=identicon&s={size}'

    def is_following(self, user: Self) -> bool:
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0

    def follow(self, user: Self) -> bool:
        if not self.is_following(user):
            self.followed.append(user)
            db.session.commit()
            return True
        return False

    def unfollow(self, user: Self) -> bool:
        if self.is_following(user):
            self.followed.remove(user)
            db.session.commit()
            return True
        return False
    
    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id = self.id)
        return followed.union(own).order_by(Post.timestamp.desc())


@login_manager.user_loader
def load_user(id: int):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=True)
    body = db.Column(db.String(512), nullable=False)
    timestamp = db.Column(db.DateTime, default=dt.now(UTC))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
        
    def __repr__(self) -> str:
        return f"<Post '{self.id}:{self.body}'>"


# class Comment(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     parent = db.Column(db.ForeignKey('comment.id'), nullable=True)
#     body = db.Column(db.String(256), nullable=False)
#     post = db.Column(db.ForeignKey('post.id'), nullable=False)
#     user = db.Column(db.ForeignKey('user.id'), nullable=False)
#     timestamp = db.Column(db.DateTime, default=dt.now(UTC))

#     post = db.relationship('Post', backref='comments', lazy='select')
#     comment = db.relationship('Comment', backref='replies', lazy='select')

#     def __repr__(self) -> str:
#         return f"<Comment '{self.id}:{self.body}'>"


class PasswordResetTokens(db.Model):
    # TODO: use blacklist methoad to revoke tokens instead of tracking valid tokens
    id = db.Column(db.Integer, primary_key=True)
    _token = db.Column(db.String(256), nullable=False)
    _expire_time = db.Column(db.DateTime, nullable=False)

    @classmethod
    def generate(cls, user: User, expires_in: int = 600):
        token = {
            "reset_password": user.id,
            "exp": dt.now(UTC) + td(seconds=expires_in)
        }
        instence = cls(
            _token=jwt.encode(token, flask_app.config["SECRET_KEY"], algorithm="HS256"),
            _expire_time = token["exp"]
        )
        db.session.add(instence)
        db.session.commit()
        return instence._token
    
    @classmethod
    def validate(cls, token: str):
        if not cls.query.filter_by(_token=token).first():
            return None
        # remove expired tokens
        cls.query.filter(cls._expire_time < dt.now(UTC)).delete()
        db.session.commit()
        try: # validate token
            id = jwt.decode(token, flask_app.config["SECRET_KEY"], algorithms="HS256")["reset_password"]
            user = User.query.get(id)
            if not user:
                return None
            return user
        except:
            return None

    @classmethod
    def use(cls, token: str):
        try:
            user = cls.validate(token=token)
            if not user:
                return None
            cls.query.filter_by(_token=token).delete()
            db.session.commit()
            return user
        except:
            cls.query.filter_by(_token=token).delete()
            cls.query.filter(cls._epxire_time < dt.now(UTC)).delete()
            db.session.commit()
            return None


class GalleryPost(db.Model):
    __tablename__ = 'gallerypost'
    # TODO: create galary listings
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=dt.now(UTC))
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(512), nullable=True)
    author = db.relationship('User', backref='gallery_post', uselist=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return f'<GalleryPost {self.id}:{self.title}'


class GalleryPostImages(db.Model):
    __tablename__ = 'galleryimages'
    # TODO: one to many relationship
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(256), nullable=False)

    posts = db.relationship('GalleryPost', backref='images', uselist=False)
    gallerypost_id = db.Column(db.Integer, db.ForeignKey('gallerypost.id'))


