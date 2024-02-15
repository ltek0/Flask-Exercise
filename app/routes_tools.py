from urllib.parse import urlsplit, urlparse

from flask import url_for
 
def get_next_url_from_request(request):

    next_url = request.args.get('next')
    
    # check if next url is not specified
    if not next_url or urlsplit(next_url).netloc != '':
        
        next_url = request.referrer
        print(next_url)
        # check if referrer is not from the same domain or same path or empty
        if not next_url or urlsplit(next_url).path == request.path or urlsplit(next_url).netloc != urlparse(request.url_root).netloc:

            next_url = url_for('index')

    return next_url

def us():
    
    # try to get next_url from session
    # if not found and is GET request(get login page)
    # get next_url from request and store in session
    # redefine new next_url from session
    
    next_url = session.get('next_url', None)
    if request.method == 'GET' and not next_url:
        session['next_url'] = routes_tools.get_next_url_from_request(request)
    next_url = session.get('next_url')