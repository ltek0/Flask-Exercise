from flask import render_template, request
from flask_login import current_user
from datetime import datetime as dt

from app import flask_app
from app.models import Post
import inspect


@flask_app.before_request
def before_request():
    # update last seen
    if current_user.is_authenticated:
        current_user.update_last_seen(dt)


@flask_app.route('/')
@flask_app.route('/index')
@flask_app.route('/abc')
def index():
    posts = Post.query.order_by(Post.timestamp.desc()).limit(10).all()
    return render_template('index.html.j2', title='Home', posts=posts)




def get_attributes(obj):
    attributes = {}

    for attribute_name in dir(obj):
        if attribute_name.startswith('_'):
            continue

        try:
            attribute_value = getattr(obj, attribute_name)

            if inspect.ismethod(attribute_value) or inspect.isclass(attribute_value):
                attributes[attribute_name] = get_attributes(attribute_value)
            elif isinstance(getattr(type(obj), attribute_name, None), property):
                attributes[attribute_name] = attribute_value
            else:
                attributes[attribute_name] = attribute_value
        except Exception:
            pass

    if attributes or attributes != {}:
        return attributes 
    else:
        return ''

@flask_app.route('/debug')
def debug_url():
    request_attributes = get_attributes(request)
    return render_template('debug.html.j2', req_atr=request_attributes)

from app import routes_user, routes_tools