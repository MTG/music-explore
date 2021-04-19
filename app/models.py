from copy import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import yaml
from annoy import AnnoyIndex
from flask import Blueprint, current_app, g

bp = Blueprint('models', __name__)


@dataclass
class Model:
    data: dict
    dataset: str
    architecture: str
    layer: str
    projection: Optional[str]

    def __repr__(self):
        suffix = f'-{self.projection}' if self.projection else ''
        return f'{self.dataset}-{self.architecture}-{self.layer}' + suffix

    @property
    def dataset_data(self):
        return self.data['datasets'][self.dataset]

    @property
    def architecture_data(self):
        return self.data['architectures'][self.architecture]

    @property
    def layer_data(self):
        return self.architecture_data['layers'][self.layer]

    @property
    def index_file(self):
        return Path(current_app.config['INDEX_DIR']) / f'{self}.ann'

    @property
    def length(self):
        return self.architecture_data['segment-length']

    @property
    def n_dimensions(self):
        return self.layer_data['size'] if self.projection != 'tsne' else 2

    def with_projection(self, projection):
        new_model = copy(self)
        new_model.projection = projection
        return new_model

    def without_projection(self):
        new_model = copy(self)
        new_model.projection = None
        return new_model

    def get_annoy_index(self):
        if not hasattr(self, 'index'):
            self.index = AnnoyIndex(self.layer_data['size'], current_app.config['ANNOY_DISTANCE'])
            self.index.load(str(self.index_file))
        return self.index

    def get_embeddings_from_annoy(self, tracks, dimensions=None):
        self.get_annoy_index()
        embeddings = []
        for track in tracks:
            track_embeddings = [self.index.get_item_vector(segment.id) for segment in track.get_segments(self.length)]
            track_embeddings = np.array(track_embeddings)
            if dimensions is not None:
                track_embeddings = track_embeddings[:, dimensions]
            embeddings.append(track_embeddings)
        return embeddings

    def get_embeddings_from_file(self, tracks, dimensions=None):
        # alternative way of reading from file, is 2x faster
        embeddings_dir = Path(current_app.config['DATA_DIR']) / str(self)
        if dimensions is None:
            return [track.get_embeddings_from_file(embeddings_dir) for track in tracks]

        return [track.get_embeddings_from_file(embeddings_dir)[:, dimensions] for track in tracks]

    def get_embeddings_from_aggrdata(self, tracks, dimensions=None):
        embeddings_file = Path(current_app.config['AGGRDATA_DIR']) / f'{self}.npy'
        embeddings = np.load(embeddings_file, mmap_mode='r')
        if dimensions is None:
            return [embeddings[track.get_aggrdata_slice()] for track in tracks]

        return [embeddings[track.get_aggrdata_slice(self.length), dimensions] for track in tracks]


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
        """Returns combinations of dataset, architecture, and layer ignoring projections"""
        for architecture, architecture_data in self.data['architectures'].items():
            for dataset in architecture_data['datasets']:
                for layer in architecture_data['layers']:
                    yield Model(self.data, dataset, architecture, layer, projection=None)

    def get_offline_projections(self, projection):
        """Returns all models that with specified projection"""
        for model in self.get_combinations():
            yield model.with_projection(projection)

    def get_all_offline_projections(self):
        """Returns all models that are projections"""
        for projection in self.data['offline-projections']:
            yield from self.get_offline_projections(projection)

    def get_all_offline(self):
        yield from self.get_combinations()
        yield from self.get_all_offline_projections()

    def get_comparable_models(self, length):
        ...


def get_models():
    if 'models' not in g:
        models_file = current_app.config['MODELS_FILE']
        with current_app.open_resource(models_file) as fp:
            g.models = Models(yaml.safe_load(fp))
    return g.models


@bp.route('/metadata')
def get_metadata():
    return get_models().data
