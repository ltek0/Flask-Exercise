import werkzeug.security
from datetime import datetime as dt, UTC, timedelta as td
from typing import Self
import jwt
from hashlib import md5

from flask_login import UserMixin

from . import db, login_manager, flask_app, google_cloud


followers = db.Table(
    'Followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class UserRole(db.Model):
    __tablename__ = 'userroles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self) -> str:
        return f'<UserRole {self.id}:{self.name}>'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False,
                         index=True, unique=True)
    email = db.Column(db.String(128), nullable=False, index=True, unique=True)
    _password_hash = db.Column(db.String(256), nullable=False, index=True)
    last_seen = db.Column(db.DateTime, nullable=True)
    display_name = db.Column(db.String(100), nullable=True)
    about_me = db.Column(db.String(256), nullable=True)
    role_id = db.Column(db.ForeignKey('userroles.id'))

    posts = db.relationship('Post', backref='author', lazy='select')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __init__(self, username: str, email: str, display_name: str = None, about_me: str = None, role_name: str = 'User'):
        self.username = username
        self.email = email
        self.display_name = display_name or self.username
        self._about_me = about_me or '---'
        self.role = UserRole.query.filter_by(name=role_name).first()
        if not self.role:
            self.role = UserRole(name=role_name)
            db.session.add(self.role)

    def __repr__(self) -> str:
        return f'<User {self.id}:{self.username}>'

    def set_password(self, password: str) -> None:
        self._password_hash = werkzeug.security.generate_password_hash(
            password)

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
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())
    
    def has_role(self, role: str) -> bool:
        return self.role.name == role


@login_manager.user_loader
def load_user(id: int):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=True)
    body = db.Column(db.String(512), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: dt.now(UTC))
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
            _token=jwt.encode(
                token, flask_app.config["SECRET_KEY"], algorithm="HS256"),
            _expire_time=token["exp"]
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
        try:  # validate token
            id = jwt.decode(token, flask_app.config["SECRET_KEY"], algorithms="HS256")[
                "reset_password"]
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
        except Exception:
            cls.query.filter_by(_token=token).delete()
            cls.query.filter(cls._epxire_time < dt.now(UTC)).delete()
            db.session.commit()
            return None


class GalleryCategory(db.Model):
    __tablename__ = 'gallerycategory'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f'<GalleryPost {self.id}:{self.name}>'


class GalleryPost(db.Model):
    __tablename__ = 'gallerypost'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: dt.now(UTC))
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(512), nullable=True)
    _views = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    _is_ready = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.ForeignKey('gallerycategory.id'))
    author = db.relationship('User', backref='gallery_post', uselist=False)
    category = db.relationship(
        'GalleryCategory', backref='post', uselist=False)

    def __init__(self, title: str, description: str, author: User, category: str):
        self.title = title
        self.description = description
        self.author = author
        self.category = GalleryCategory.query.filter_by(name=category).first()
        if not self.category:
            self.category = GalleryCategory(name=category)
            db.session.add(self.category)
        self._is_ready = False

    def __repr__(self) -> str:
        return f'<GalleryPost {self.id}:{self.title}>'

    @property
    def views(self):
        return self._views

    def view(self):
        self._views += 1
        db.session.commit()

    @property
    def is_ready(self):
        if self._is_ready:
            return True
        for image in self.images.all():
            if not google_cloud.BucketObject(object_key=image.object_key).exist:
                return False
        self._is_ready = True
        db.session.commit()
        return self.is_ready


class GalleryPostImage(db.Model):
    __tablename__ = 'gallerypostimage'
    id = db.Column(db.Integer, primary_key=True)
    object_key = db.Column(db.String(40), nullable=False, unique=True)
    post = db.relationship('GalleryPost', backref='images', uselist=False)
    gallerypost_id = db.Column(db.Integer, db.ForeignKey('gallerypost.id'))

    def __repr__(self) -> str:
        return f'<GalleryPostImages {self.id}:{self.path}>'

    @property
    def path(self):
        return f"https://storage.googleapis.com/{flask_app.config['GOOGLE_STORAGE_BUCKET']}/{self.object_key}"


#----------------------------------------------------------------------------------
class SecondHandPost(db.Model):
    __tablename__ = 'secondhandpost'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    _queries = db.Column(db.Integer, default=0)
    _views = db.Column(db.Integer, default=0)
    issue_date = db.Column(db.DateTime, default=lambda: dt.now(UTC))
    description = db.Column(db.String(512), nullable=False)
    seller = db.relationship('User', backref='second_hand_post', uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    category_id = db.Column(db.ForeignKey('secondhandcategory.id'))
    _category = db.relationship('SecondHandCategory', backref='posts', uselist=False)
    type = db.Column(db.String(20), nullable=False)

    def __repr__(self) -> str:
        return f'<SecondHandPost {self.id}:{self.title}>'

    @property
    def category(self) -> str:
        return self._category.name or 'other'
    
    @category.setter
    def category(self, category_string: str):
        self._category = SecondHandCategory.query.filter_by(name=category_string).first()
        if not self._category:
            self._category = SecondHandCategory(name=category_string)
            db.session.add(self._category)

    @property
    def views(self):
        return self._views

    def add_view_count(self):
        self._views += 1
        db.session.commit()

    @property
    def queries(self):
        return self._queries

    def add_queries_count(self):
        self._queries += 1
        db.session.commit()


class SecondHandImage(db.Model):
    __tablename__ = 'secondhandimage'
    id = db.Column(db.Integer, primary_key=True)
    object_key = db.Column(db.String(40), nullable=False, unique=True)
    post = db.relationship('SecondHandPost', backref='images', uselist=False)
    secondhandpost_id = db.Column(db.Integer, db.ForeignKey('secondhandpost.id'))

    def __repr__(self) -> str:
        return f'<secondhandimage {self.id}:{self.path}>'

    @property
    def path(self):
        return f"https://storage.googleapis.com/{flask_app.config['GOOGLE_STORAGE_BUCKET']}/{self.object_key}"
    

class SecondHandCategory(db.Model):
    __tablename__ = 'secondhandcategory'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True, index=True)

    def __repr__(self) -> str:
        return f'<SecondHandCategory {self.id}:{self.name}>'


#----------------------------------------------------------------------------------
class TravelBlog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=dt.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'), nullable=False)

    user = db.relationship('User', backref='travel_blogs', lazy=True)
    country = db.relationship('Country', backref='travel_blogs', lazy=True)
    city = db.relationship('City', backref='travel_blogs', lazy=True)

    def __repr__(self) -> str:
        return f"<TravelBlog '{self.id}:{self.title}'>"

    def __init__(self, title, content, country, city, user):
        self.title = title
        self.content = content
        self.country = country
        self.city = city
        self.user = user

    @staticmethod
    def create_or_get_country(name):
        country = Country.query.filter_by(name=name).first()
        if not country:
            country = Country(name=name)
            db.session.add(country)
            db.session.commit()  # Commit the changes to the database
        return country

    @staticmethod
    def create_or_get_city(name):
        city = City.query.filter_by(name=name).first()
        if not city:
            city = City(name=name)
            db.session.add(city)
            db.session.commit()  # Commit the changes to the database
        return city

    def save(self):
        country = self.create_or_get_country(self.country_name)
        city = self.create_or_get_city(self.city_name)

        self.country = country
        self.city = city

        db.session.add(self)
        db.session.commit()


class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    def __repr__(self) -> str:
        return f"Country('{self.name}')"


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    def __repr__(self) -> str:
        return f"City('{self.name}')"

#----------------------------------------------------------------------------------