import os


basedir = os.path.abspath(os.path.dirname(__file__))


def _required_env(name: str):
    '''Used when a environment variable is required to be set'''
    try:
        env = os.environ[name]
    except KeyError:
        raise ValueError(f"{name} is not set in enviroment")
    return env

class Config(object):
    
    SECRET_KEY = _required_env("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = _required_env('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = _required_env('MAIL_SERVER')
    MAIL_PORT = int(_required_env('MAIL_PORT'))
    MAIL_USE_TLS = bool(os.environ.get('MAIL_USE_TLS'))
    MAIL_USE_SSL = bool(os.environ.get('MAIL_USE_SSL'))
    MAIL_SENDER = _required_env('MAIL_SENDER')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    SERVER_NAME = _required_env('SERVER_NAME')

    POSTS_PER_PAGE = 3
    LANGS = ['en', 'zh']
    PASSWORD_RESET_EXPIRE = 600
    
    # TODO: migrate to database user role
    ADMINS = ['admin@local']