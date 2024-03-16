from flask import render_template

from . import flask_app, db


@flask_app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html.j2"), 404


@flask_app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("errors/500.html.j2"), 500
