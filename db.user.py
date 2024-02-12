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

def create_user(u: models.User):
    return u.create()

def print_user_info(u: models.User):
    print(f'{u.id}, {u.username}, {u.email}')

def demo():
    random_user = new_random_user()
    user = create_user(random_user)
    print_user_info(user)
    print(user.check_password('abcd'))
    print(user.set_password('abcd'))
    print(user.check_password('abcd'))
    print(user.check_password('abcde'))

if __name__ == '__main__':
    demo()