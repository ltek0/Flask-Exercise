from typing import Optional
from datetime import datetime as dt, timezone as tz

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

    def create(self):
        try:
            db.session.add(self)
            db.session.commit()
            return self
        except Exception as ex:
            print(ex)
            return None
        
        
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