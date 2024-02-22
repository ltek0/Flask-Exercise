from flask import render_template, request, url_for
from app import flask_app
import inspect


@flask_app.route('/')
@flask_app.route('/index')
def index():
    posts = [
        {
            'author': {'username': 'user2'},
            'body': 'Post 1'
        },
        {
            'author': {'username': 'user3'},
            'body': 'Post 2'
        }
    ]
    return render_template('index.html', title='Home', posts=posts)


@flask_app.errorhandler(404)
def page_not_found(e):
    print('error 404')
    last_url = request.referrer or url_for('index')
    return render_template('404.html', last_purl = last_url), 404

@flask_app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


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
    return render_template('debug.html', req_atr=request_attributes)

from app import routes_user, routes_tools