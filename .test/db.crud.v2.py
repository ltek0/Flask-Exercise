from app import models, flask_app, db
from timeit import default_timer as timer
import sqlalchemy as sa
from faker import Faker

def create_user(user: models.User):
    return user.create()

def generate_random_user() -> models.User:
    faker = Faker()
    u = {
        'username': faker.user_name(),
        'email': faker.email()
    }
    return models.User(**u)

def print_user_info(u: models.User) -> None:
    print(f'''ID: {u.id}
Username: {u.username}
Email: {u.email}''')

def create_and_print_new_random_user_info():
    start = timer()
    new_user = generate_random_user().create()
    end = timer()

    if new_user:
        print_user_info(new_user)
        print(f'Time consumed: {str(end - start)[:5]}\n') 
    else:
        raise('cannot create user')

def stress_create(c: int):
    for i in range(c):
        print(f'count {i}')    
        create_and_print_new_random_user_info()
        
if __name__ == '__main__':
    flask_app.app_context().push()
    