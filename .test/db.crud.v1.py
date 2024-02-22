from app import models, flask_app, db
import sqlalchemy as sa
import uuid

def create_user(u: models.User)  -> None:
    db.session.add(u)
    db.session.commit()

def select_all_from_model(model: models):
    q = sa.select(model)
    return db.session.scalars(q).all()

def print_user_info(u: models.User) -> None:
    print(f'''ID: {u.id}
Username: {u.username}
Email: {u.email}
''')

def print_all_user_info() -> None:
    users = select_all_from_model(models.User)
    for i in users:
        print_user_info(i)

def create_random_user(count: int) -> None:
    for i in range(1, count+1):
        r_uname = f'r_{str(uuid.uuid4())[:8]}'
        u = models.User(
            username = r_uname,
            email = f'{r_uname}@random.user'
        )
        create_user(u)
        print(f'{i}. {u}')

if __name__ == '__main__':
    flask_app.app_context().push()

    #user_info = {
    #    'username': 'karl',
    #    'email': 'karl@testing'
    #}
    #user = models.User(**user_info)

    #create_user(user)
    #print(select_all_from_model(models.User))
    #create_random_user(100000)
    #print_all_user_info()


    u = User(
        usermame = 'karl'
        email = '..'
    )
    db.session.add(u)
    db.session.commit()