from app import flask_app

from db_migtions import db_migrations

if __name__ == "__main__":
    db_migrations()
    flask_app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True
    )