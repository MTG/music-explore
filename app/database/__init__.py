from .base import db, init_db_command


def init_app(app):
    db.init_app(app)
    app.cli.add_command(init_db_command)
