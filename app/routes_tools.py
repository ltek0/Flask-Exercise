from urllib.parse import urlsplit, urlparse

from flask import url_for
 
def get_next_url_from_request(request):

    # check for next url in args
    next_url = request.args.get('next', None)

    #if not present or domain not the same
    if not next_url or urlparse(next_url).netloc != urlparse(request.url).netloc:

        # if not the same as current url
        if request.referrer != request.url:
            # return index if treferrer is empty 
            return request.referrer or url_for('index')
            
    # has next url and checks out
    return next_url