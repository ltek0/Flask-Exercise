from flask import render_template, flash

from . import flask_app, db


@flask_app.errorhandler(404)
def not_found_error(error: str):
    return render_template('errors/404.html.j2'), 404


@flask_app.errorhandler(403)
def no_permission_error(error: str):
    flash(error)
    return render_template('errors/403.html.j2'), 403


@flask_app.errorhandler(500)
def internal_error(error: str):
    db.session.rollback()
    return render_template('errors/500.html.j2'), 500