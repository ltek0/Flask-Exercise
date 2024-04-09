# load env must be placed before app import
from dotenv import load_dotenv
load_dotenv('.flaskenv')

from os import path as op
import subprocess

from app import db
from app.models import User, Post
from app import flask_app


def _warning():
    print('Warning!!! This will remove all post and users from the database')
    pros = input('Wish to proseed(y/N)')
    if pros == 'y':
        db.create_all()
        db.drop_all()
        return True
    return False


def _create_users(count: int):
    for i in range(count):
        user = User(
            display_name = f'User{i+1} name',
            username = f'user{i+1}',
            email = f'user{i+1}@example.com')
        user.set_password(f'user{i+1}pw')
        db.session.add(user)
        db.session.commit()
        print(user)


def _create_post_for_user(u: User, count: int):
    for i in range(count):
        post = Post(
            title = f"post{i+1}",
            body = f'''Body of post{i+1} for user with username: {u.username}''',
            author = u
        )
        db.session.add(post)
        db.session.commit()
        print(post)
    

if __name__ == '__main__':

    flask_app.app_context().push()

    if not _warning():
        raise Exception('Exit on cancel')
    
    if not op.exists(op.join(op.dirname(op.realpath(__file__)), 'migrations')):
        subprocess.run(['flask', 'db', 'init'])
    subprocess.run(['flask', 'db', 'migrate'])
    subprocess.run(['flask', 'db', 'upgrade'])
    _create_users(5)

    user1 = db.session.query(User).filter_by(username='user1').first()
    user2 = db.session.query(User).filter_by(username='user2').first()
    user3 = db.session.query(User).filter_by(username='user3').first()
    user4 = db.session.query(User).filter_by(username='user4').first()
    user5 = db.session.query(User).filter_by(username='user5').first()

    _create_post_for_user(user1, 5)
    _create_post_for_user(user2, 5)
    _create_post_for_user(user3, 5)
    _create_post_for_user(user4, 5)
    _create_post_for_user(user5, 5)

    user1.follow(user4)
    user1.follow(user5)

    user2.follow(user5)
    user2.follow(user1)

    user3.follow(user1)
    user3.follow(user2)    

    user4.follow(user2)
    user4.follow(user3)

    user5.follow(user3)
    user5.follow(user4)