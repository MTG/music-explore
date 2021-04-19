import logging

import click
import numpy as np
import pandas as pd
import plotly.express as px
from flask.cli import with_appcontext

from app.database.base import Track
from app.models import get_models

from .statistics import FLOAT_FORMAT

RETURN_VALUES = ['k_skewness', 'k_skewness_truncnorm', 'atkinson', 'gini', 'robinhood', 'antihub_occurrence',
                 'hub_occurrence', 'groupie_ratio']


def measure_hubness(n_tracks, output_file, metric, projection, dimensions, n_jobs, random):
    from skhubness import Hubness
    tracks = Track.get_all(limit=n_tracks, random=random)

    models = get_models()
    models_iter = models.get_combinations() if projection is None else models.get_offline_projections(projection)
    results = {}
    for model in models_iter:
        embeddings = model.get_embeddings_from_file(tracks)
        embeddings_stacked = np.vstack(embeddings)

        hub = Hubness(k=10, metric=metric, return_value='all', n_jobs=n_jobs)
        hub.fit(embeddings_stacked[:, :dimensions])
        results[str(model)] = {key: value for key, value in hub.score().items() if key in RETURN_VALUES}
        logging.info(f'{model} done')

    results_df = pd.DataFrame.from_dict(results, orient='index')
    results_df.to_csv(output_file, float_format=FLOAT_FORMAT)


def visualize_hubness(input_file):
    results = pd.read_csv(input_file, index_col=0, comment='#')
    fig = px.line(results)
    fig.show()


@click.command('measure-hubness')
@click.option('-n', '--n-tracks', type=int)
@click.option('-o', '--output-file', type=click.Path())
@click.option('-m', '--metric', default='cosine', type=str)
@click.option('-p', '--projection', default=None, type=str)
@click.option('-d', '--dimensions', default=None, type=int)
@click.option('-j', '--n-jobs', default=8, type=int)
@click.option('-r', '--random', is_flag=True)
@with_appcontext
def measure_hubness_command(n_tracks, output_file, metric, projection, dimensions, n_jobs, random):
    measure_hubness(n_tracks, output_file, metric, projection, dimensions, n_jobs, random)


@click.command('visualize-hubness')
@click.argument('input_file')
def visualize_hubness_command(input_file):
    visualize_hubness(input_file)
