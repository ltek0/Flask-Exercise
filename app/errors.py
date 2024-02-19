from app import flask_app
from flask import request, render_template, url_for

@flask_app.errorhandler(404)
def page_not_found(e):
    print('error 404')
    last_url = request.referrer or url_for('index')
    return render_template('404.html.j2', last_purl = last_url), 404

@flask_app.errorhandler(500)
def internal_error(error):
    return render_template('500.html.j2'), 500
