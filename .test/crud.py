from app import models, db

from typing import List, Optional

import sqlalchemy as sa

class post:
    @classmethod
    def get_latest_Posts(n: int) -> List['models.Post']:
        return models.Post.query.order_by(models.Post.timestamp.desc()).limit(n).all()

class user:
    @classmethod
    def verification(cls, uname_or_email: str, passowrd: str) -> Optional['models.User']:

        u = models.User.query.filter_by(sa.or_(models.User.email == uname_or_email, models.User.username == uname_or_email)).first()

        if u and u.check_password(passowrd):
            return u
        
        return None