from .extract import extract


def init_app(app):
    app.cli.add_command(extract)
