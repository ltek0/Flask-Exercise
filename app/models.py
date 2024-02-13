from typing import Optional
from datetime import datetime as dt, timezone as tz
from werkzeug import security
from re import fullmatch

import sqlalchemy as sa
import sqlalchemy.orm as so

from app import db
from app import flask_app
from app import login

from flask_login import UserMixin

@login.user_loader
def load_user(id: int) -> Optional['User']:
    return db.session.get(User, id)


class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')

    def __repr__(self) -> str:
        return f'<User {self.id}:{self.username}>'
    
    def check_password(self, password: str) -> bool:
        return security.check_password_hash(self.password_hash, password)
    
    def set_password(self, p: str):
        self.password_hash = security.generate_password_hash(p)
    
    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

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
        
