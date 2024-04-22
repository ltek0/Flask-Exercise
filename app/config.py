import os
basedir = os.path.abspath(os.path.dirname(__file__))


def _required_env(name: str):
    '''Used when a environment variable is required to be set'''
    try:
        env = os.environ[name]
    except KeyError as exc:
        raise KeyError(f"{name} is not set in environment") from exc
    return env


class Config:

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

    # server_name used by url_for to construct url
    # without it will resault in
    # indirect-access(email) having 127.0.0.1:<-port-> as host
    _svr_nme = os.environ.get('SERVER_NAME')
    if _svr_nme:
        SERVER_NAME = _svr_nme

    POSTS_PER_PAGE = 3
    LANGS = ['en', 'zh']
    PASSWORD_RESET_EXPIRE = 600

    # TODO: migrate to database user role
    ADMINS = ['admin@local']

    GOOGLE_SERVICE_ACCOUNT_FILE = _required_env('GOOGLE_SERVICE_ACCOUNT_FILE')
    GOOGLE_STORAGE_BUCKET = _required_env('GOOGLE_STORAGE_BUCKET')
    IS_DEV_LOCAL = bool(os.environ.get('IS_DEV_LOCAL'))

    ALLOWED_IMAGE_FORMATS = ['jpg', 'png', 'gif', 'jfif']
    IMAGE_PER_GALLERY = 50
    IMAGE_PER_UPLOAD = 20