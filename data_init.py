from faker import Faker
import csv

class User:
    def __init__(self, username: str, email: str, password: str):
        self.username = username
        self.email = email
        self.password = password

class Post:
    def __init__(self, title: str, body: str, author: User):
        self.title = title
        self.body = body
        self.author = author


def random_fake_user():
    fake = Faker()
    return User(
        username = fake.user_name(),
        email = fake.email(),
        password= fake.password()  
    )

def write_random_users_to_csv():
    with open('users.csv', 'w') as file:
        writer = csv.writer(file)
        users = []

        # create n users
        for i in range(10):
            u = random_fake_user()
            users.append([u.username, u.email, u.password])

        # write users to csv
        writer.writerows(users)

def create_user_in_csv():
    with open("users.csv", 'r') as file:
        users = []
        reader = csv.DictReader(file)
        
        User(id=1)


if __name__ == '__main__':
    write_random_users_to_csv()
    