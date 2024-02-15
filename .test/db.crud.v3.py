from app import models, flask_app, db
import sqlalchemy as sa
from faker import Faker

flask_app.app_context().push()

def new_random_user():
    faker = Faker()
    u = {
        'username': faker.user_name(),
        'email': faker.email()
    }
    return models.User(**u)

#### creation: user/post
def create_user(u: models.User):
    return u.create()

def create_post(body: str, author: models.User):
    p = models.Post(body = body, author = author)
    return p.create()

#### get
def get_all_users():
    q = sa.select(models.User)
    return db.session.scalars(q).all()
    
def get_user_from_id(id: int) -> models.User:
    return db.session.get(models.User, id)

def get_all_posts():
    q = sa.select(models.Post)
    return db.session.scalars(q).all()

def get_post_from_id(id: int) -> models.Post:
    return db.session.get(models.Post, id)

def get_posts_from_user(u: models.User):
    q = u.posts.select()
    return db.session.scalars(q).all()

    
#### print INFO
def print_user_info(u: models.User):
    print(f'{u.id}, {u.username}, {u.email}')

def print_post_info(p: models.Post):
    print(f'{p.id}, {p.timestamp}, [{p.author.id}, {p.author.username}], {p.body}')


if __name__ == '__main__':
    '''
    random_user = new_random_user()
    user = create_user(random_user)
    print_user_info(user)
    new_post = {
        'body': 'test_post',
        'author': user
    }
    post = create_post(**new_post)
    print_post_info(post)

# get all users in reverse alphabetical order
>>> query = sa.select(User).order_by(User.username.desc())
>>> db.session.scalars(query).all()
[<User susan>, <User john>]

# get all users that have usernames starting with "s"
>>> query = sa.select(User).where(User.username.like('s%'))
>>> db.session.scalars(query).all()
[<User susan>]

'''