from app import db, login_manager
import werkzeug.security
from datetime import datetime as dt

from flask_login import UserMixin

from hashlib import md5

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    _display_name = db.Column(db.String(100)) 
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(128), index=True, unique=True, nullable=False)
    _passowrd_hash = db.Column(db.String(256), index=True)
    about_me = db.Column(db.String(256))
    last_seen = db.Column(db.DateTime, default=lambda: dt.utcnow)
    posts = db.relationship('Post', backref='author', lazy='select')

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
        return f'<Post {self.title}>'