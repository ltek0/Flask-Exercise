from flask import request, render_template, url_for
from urllib.parse import urlparse
from app import flask_app
import inspect

 
def get_next_url_from_request(request):

    # check for next url in args
    next_url = request.args.get('next', None)

    #if not present or domain not the same
    if not next_url or urlparse(next_url).netloc != urlparse(request.url).netloc:

        # if not the same as current url
        if request.referrer != request.url:
            # return index if treferrer is empty 
            return request.referrer or url_for('index')

        else:
            # request.referrer same
            return  url_for('index')

    # has next url and checks out
    return next_url



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