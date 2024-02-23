from flask import render_template

from flask_login import current_user
 
from app import flask_app
from app.models import Post
import inspect


@flask_app.route('/')
@flask_app.route('/index')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).limit(10).all()
    return render_template('index.html.j2', title='Home', posts=posts)


@flask_app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@flask_app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


from app import routes_user, routes_tools, routes_post