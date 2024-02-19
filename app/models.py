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

########################################################################################
# setting password with .password = 'pass' using property and setter
    _password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), index=True)
    @property
    def password(self):
        raise Exception('Password cannot be directly called!')
    
    @password.setter
    def password(self, new_password: str):
        self._password_hash = security.generate_password_hash(new_password)
########################################################################################

########################################################################################
# display name are private and shoudld not be called, accessed with property
    _display_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(24))
    @property
    def display_name(self):
        if not self._display_name:
            return self.username
        return self._display_name
    
    @display_name.setter
    def display_name(self, new_dname: str):
        if new_dname and len(new_dname) > 24:
            raise Exception('Display Name too long. Limit 24 charactors')
        if not new_dname:
            self._display_name = ''
        self._display_name = new_dname
########################################################################################

########################################################################################
# set the bio to empty string when not specified
    _bio: so.Mapped[Optional[str]] = so.mapped_column(sa.String(30))
    @property
    def bio(self):
        if not self._bio:
            return ''
        return self._bio
    
    @bio.setter
    def bio(self, new_bio):
        if new_bio and len(new_bio) > 30:
            raise Exception('Display Name too long. Limit 24 charactors')
        self._bio = new_bio
########################################################################################





    last_seen: so.Mapped[dt] = so.mapped_column(default=lambda: dt.now(tz.utc))

    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')





########################################################################################
# methoad calles
    def __repr__(self) -> str:
        return f'<User {self.id}:{self.username}>'

    def avatar(self, size: int = 50) -> str:
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    # true when password_hash are same as impited
    def check_password(self, password: str) -> bool:
        return security.check_password_hash(self._password_hash, password)
    
    #
    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as ex:
            print(ex)
            return None

    def update_last_seen(self, datetime: dt):
        self.last_seen = dt.utcnow()
        print(f'user {self.username} logged in at UTC:{self.last_seen}')
        db.session.commit()



class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column( primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(200), index=True)
    timestamp: so.Mapped[dt] = so.mapped_column(default=lambda: dt.now(tz.utc), index=True)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    
    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self) -> str:
        return f'<Post {self.id}:{self.body}>'
