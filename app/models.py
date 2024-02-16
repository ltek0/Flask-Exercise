from typing import Optional
from datetime import datetime as dt, timezone as tz
from werkzeug import security
from hashlib import md5

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db
from app import login

from flask_login import UserMixin

@login.user_loader
def load_user(id: int) -> Optional['User']:
    return db.session.get(User, id)


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(256), index=True)


    _display_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(32))
    @property
    def display_name(self):
        if not self._display_name:
            return self.username
        return self._display_name
    
    @display_name.setter
    def display_name(self, new_dname):
        if new_dname == '':
            self._display_name = None
        else:
            self._display_name = new_dname
    
    _bio: so.Mapped[Optional[str]] = so.mapped_column(sa.String(30))
    @property
    def bio(self):
        if not self._bio:
            return 'Just a Regular User.'
        return self._bio
    @bio.setter
    def bio(self, new_bio):
        self._bio = new_bio    

    last_seen: so.Mapped[Optional[dt]] = so.mapped_column(default=lambda: dt.now(tz.utc))
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')

    def __repr__(self) -> str:
        return f'<User {self.id}:{self.username}>'

    def avatar(self, size: int = 50) -> str:
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def check_password(self, password: str) -> bool:
        return security.check_password_hash(self.password_hash, password)
    
    def set_password(self, p: str):
        self.password_hash = security.generate_password_hash(p)
    
    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as ex:
            print(ex)
            return None

    def update_last_seen(self, user_id: int):
        user = User.query.get(user_id)
        return user.last_seen



class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column( primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(200), index=True)
    timestamp: so.Mapped[dt] = so.mapped_column(default=lambda: dt.now(tz.utc), index=True)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    
    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self) -> str:
        return f'<Post {self.id}:{self.body}>'
