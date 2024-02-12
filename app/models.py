from typing import Optional
from datetime import datetime as dt, timezone as tz
from werkzeug import security

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db
from app import flask_app

class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')

    def __repr__(self) -> str:
        return f'<User {self.id}:{self.username}>'



##############################################################################
#
#  Note:
#     A user can be created by using .create()
#     However until a password have been set using .password 
#     the user remain in a disable state, calling check_password() 
#     will return [False, '$reason']
#
##############################################################################
    def create(self):
        
        if not hasattr(self,'username') or not self.username:
            raise('Exeception: Invalid username')
        if not hasattr(self, 'email') or not self.email:
            raise('Exeception: Invalid email')
        
        db.session.add(self)
        db.session.commit()
        return self

##############################################################################
    def set_password(self, password: str) -> bool:
        if not password:
            print('Empty Password')
            return False
        self.password_hash = security.generate_password_hash(password)
        return True

##############################################################################
    def check_password(self, password: str) -> bool:
        if not self.password_hash:
            print('Exeception: A password has not been set for the user')
            return False
        return security.check_password_hash(self.password_hash, password)
        
    
class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column( primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(200), index=True)
    timestamp: so.Mapped[dt] = so.mapped_column(default=lambda: dt.now(tz.utc), index=True)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    
    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self) -> str:
        return f'<Post {self.id}:{self.body}>'
    
    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as ex:
            print(ex)
            return None