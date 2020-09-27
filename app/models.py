from flask import g, current_app
import yaml

def init_app(app):
    if 'models_info' not in g:
        models_file = current_app.config['MODELS_FILE']
        with open(models_file) as fp:
            g.models_info = yaml.safe_load(fp)
    return g.metadata


class Model():
    def __init__(self, app, name):
        metadata_fileapp.config

class Dataset(name):
    def __init__(self):


