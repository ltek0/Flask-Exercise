from app import models, flask_app, db
import sqlalchemy as sa
from faker import Faker

flask_app.app_context().push()

def new_random_user():
    faker = Faker()
    u = {
        'username': faker.user_name(),
        'email': faker.email(),
        'password': faker.password()
    }
    return models.User(**u)

def create_user(u: models.User):
    return u.create()

def print_user_info(u: models.User):
    print(f'{u.id}, {u.username}, {u.email}, {u.password_hash}')

def demo():
    random_user = new_random_user()
    user = create_user(random_user)
    print_user_info(user)

def get_user_from_credentials():
    return models.User.get_by_credentials(username_or_email='user1', password='password1')

if __name__ == '__main__':
    for i in range(10000):
        demo()