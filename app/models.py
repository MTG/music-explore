from flask import g, current_app
import yaml
from dataclasses import dataclass
from typing import Optional

@dataclass
class Model:
    data: dict
    dataset: str
    model: str
    layer: str
    projection: Optional[str]

    def __repr__(self):
        suffix = f'-{self.projection}' if self.projection else ''
        return f'{self.dataset}-{self.model}-{self.layer}' + suffix

    @property
    def dataset_data(self):
        return self.data['datasets'][self.dataset]

    @property
    def model_data(self):
        return self.data['models'][self.model]

    @property
    def layer_data(self):
        return self.model_data['layers'][self.layer]

    # TODO: make sure that there are no issues with references
    def with_projection(self, projection):
        self.projection = projection
        return self

    def without_projection(self):
        self.projection = None
        return self


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
        """Returns combinations of dataset, model, and layer ignoring projections"""
        for model, model_data in self.data['models'].items():
            for dataset in model_data['datasets']:
                for layer in model_data['layers']:
                    yield Model(self.data, dataset, model, layer, projection=None)

    def get_offline_projections(self):
        """Returns all models that are projections"""
        for offline_projection in self.data['offline_projections']:
            for model in self.get_combinations():
                yield model.with_projection(offline_projection)

    def get_all_offline(self):
        yield from self.get_combinations()
        yield from self.get_offline_projections()


def get_models():
    if 'models' not in g:
        models_file = current_app.config['MODELS_FILE']
        with current_app.open_resource(models_file) as fp:
            g.models = Models(yaml.safe_load(fp))
    return g.models
