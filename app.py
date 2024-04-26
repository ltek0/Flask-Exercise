# load env must be placed before app import
from dotenv import load_dotenv
load_dotenv('.flaskenv')

from app import flask_app, db, models

from os import path as op
import subprocess


if __name__ == "__main__":

    if not op.exists(op.join(op.dirname(op.realpath(__file__)), 'migrations')):
        subprocess.run(['flask', 'db', 'init'])
    subprocess.run(['flask', 'db', 'migrate'])
    subprocess.run(['flask', 'db', 'upgrade'])

    flask_app.app_context().push()
    
    # if no admin, create one
    admins = models.UserRole.query.filter_by(name='admin').all()
    if not admins:
        admin = models.User(
            display_name = 'Admin',
            username = 'admin',
            email = 'admin@local',
            role_name= 'admin')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        
    flask_app.run(
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
