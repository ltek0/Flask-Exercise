from app import db, login_manager
import werkzeug.security
from datetime import datetime as dt

from flask_login import UserMixin

from hashlib import md5

followers = db.Table(
    'Followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _display_name = db.Column(db.String(100)) 
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(128), index=True, unique=True, nullable=False)
    _passowrd_hash = db.Column(db.String(256), index=True)
    about_me = db.Column(db.String(256))
    last_seen = db.Column(db.DateTime, default=lambda: dt.utcnow())
    posts = db.relationship('Post', backref='author', lazy='select')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self) -> str:
        return f'<User {self.username}>'
    
    @property
    def display_name(self) -> str:
        return self._display_name or self.username 
    
    @display_name.setter
    def display_name(self, display_name: str) -> None:
        if not display_name:
            self._display_name = self.username
        elif len(display_name) <= 100:
            self._display_name = display_name
        else:
            raise ValueError('Display name is too long')

    def set_password(self, password: str) -> None:
        self._passowrd_hash = werkzeug.security.generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return werkzeug.security.check_password_hash(self._passowrd_hash, password)

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return User.query.filter_by(username = self.username).first()
        except Exception as ex:
            db.session.rollback()
            print(ex)
            return None

    def avatar(self, size: int) -> str:
        email_md5 = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{email_md5}?d=identicon&s={size}'

    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def follow(self, user): 
        if not self.is_following(user):
            self.followed.append(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

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
    title = db.Column(db.String(128))
    body = db.Column(db.String(512))
    timestamp = db.Column(db.DateTime, default=lambda: dt.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self) -> str:
        return f"<Post '{self.body}'>"