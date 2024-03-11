from faker import Faker
import csv
from app import db
from app.model import User
from app import flask_app

flask_app.app_context().push()

class Usertmp:
    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password = password

def _random_fake_user():
    fake = Faker()
    return Usertmp(
        username = fake.user_name(),
        email = fake.email(),
        password= fake.password()  
    )

def _get_user_from_csv(file: str):
    with open(file, 'r') as file:
        reader = csv.DictReader(file)
        return list(reader)

def write_random_users_to_csv(file: str, count: int, mode: str = ''):
    if not mode or mode != 'a' or mode != 'w':
        mode = 'w'
    with open(file, mode) as file:
        writer = csv.writer(file)
        if mode == 'w':
            writer.writerow(['username','email','password'])
        for i in range(count):
            u = _random_fake_user()
            writer.writerow([u.username, u.email, u.password])
            
def create_user_from_csv(file: str):
    users = _get_user_from_csv(file)
    for us in users:
        u = User(username = us['username'], email = us['email'])
        u.set_password(us['password'])
        print(u.create_user())

def new_set_users(file: str = 'users.csv', count: int = 10):
    write_random_users_to_csv(file, count)
    User.query.delete()
    create_user_from_csv(file)

if __name__ == '__main__':
    new_set_users()