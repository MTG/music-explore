from .extract import extract_command, extract_all_command


def init_app(app):
    app.cli.add_command(extract_command)
    app.cli.add_command(extract_all_command)
