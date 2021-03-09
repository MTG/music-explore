import click
import numpy as np
from flask.cli import with_appcontext

from app.database import Track
from app.models import get_models


def measure_hubness(n_tracks):
    from skhubness import Hubness
    tracks = Track.get_all(limit=n_tracks)

    models = get_models()
    for model in models.get_combinations():
        embeddings = model.get_embeddings_from_file(tracks)
        embeddings_stacked = np.vstack(embeddings)

        hub = Hubness(k=10, metric='cosine')
        hub.fit(embeddings_stacked)
        k_skew = hub.score()
        print(f'{model},{k_skew:.3f}')


@click.command('measure-hubness')
@click.option('-n', '--n-tracks', type=int)
@with_appcontext
def measure_hubness_command(n_tracks):
    measure_hubness(n_tracks)
