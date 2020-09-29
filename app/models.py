from flask import g, current_app
import yaml


class Models:
    """Wrapper for the info from models file: detailed description of models, datasets, etc."""
    def __init__(self, data: dict):
        self.data = data

    def get_dict(self, collection: str, attribute):
        """Collapses multi-level dictionary into non-nested key-value mapping.
        For example: mtt:{name:{MTT}} -> mtt:MTT"""
        return {key: value[attribute] for key, value in self.data[collection].items()}

    def get_triplets(self, collection: str):
        """Returns list of tuples (key, name, description). Used for the convenience in templates"""
        return [(key, value['name'], value['description']) for key, value in self.data[collection].items()]

    def get_combinations(self):
        """Returns combinations of algorithm, dataset_model, layer, layer_name"""
        for model, model_data in self.data['models'].items():
            for dataset in model_data['datasets']:
                for layer, layer_data in model_data['layers'].items():
                    yield model_data['essentia-algorithm'], f'{dataset}-{model}', layer, layer_data['name']


def get_models():
    if 'models' not in g:
        models_file = current_app.config['MODELS_FILE']
        with current_app.open_resource(models_file) as fp:
            g.models = Models(yaml.safe_load(fp))
    return g.models
