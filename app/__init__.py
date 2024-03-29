import logging

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    # from werkzeug.middleware.profiler import ProfilerMiddleware
    # app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[5], profile_dir='./profile')

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

    # cache
    # TODO: lookup if we can just pass the app config and cache will ignore other options
    from .cache import cache
    cache.init_app(app, config={
        'CACHE_TYPE': app.config['CACHE_TYPE'],
        'CACHE_DEFAULT_TIMEOUT': app.config['CACHE_DEFAULT_TIMEOUT']
    })

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
    from . import models, plot, providers, similarity, views
    app.register_blueprint(views.bp)
    app.register_blueprint(plot.bp)
    app.register_blueprint(providers.bp)
    app.register_blueprint(models.bp)
    app.register_blueprint(similarity.bp)

    return app
