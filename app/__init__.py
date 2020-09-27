from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # configs
    app.config.from_mapping(
        SECRET_KEY='dev'
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # remove as much of whitespace in the templates as possible
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # database binding
    from . import database
    database.init_app(app)

    from . import processing
    processing.init_app(app)

    return app
