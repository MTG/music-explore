from flask import Flask
import logging


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

    # config our logging
    logging_level = getattr(logging, app.config['LOGGING_LEVEL'])
    logging.basicConfig(format=app.config['LOGGING_FORMAT'], level=logging_level)

    # remove as much of whitespace in the templates as possible
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    # database binding and click commands
    from . import database
    database.init_app(app)

    # processing commands
    from . import processing
    processing.init_app(app)

    # experiments
    from . import experiments
    experiments.init_app(app)

    # blueprints
    from . import views, plot, providers, models
    app.register_blueprint(views.bp)
    app.register_blueprint(plot.bp)
    app.register_blueprint(providers.bp)
    app.register_blueprint(models.bp)

    return app
