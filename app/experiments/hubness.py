import warnings

import click
import numpy as np
import pandas as pd
from flask.cli import with_appcontext
from tqdm import tqdm

from app.database.base import Track
from app.models import get_models

from .statistics import FLOAT_FORMAT

RETURN_VALUES = ['k_skewness', 'k_skewness_truncnorm', 'atkinson', 'gini', 'robinhood', 'antihub_occurrence',
                 'hub_occurrence', 'groupie_ratio']
PLOT_VALUES = ['k_skewness', 'k_skewness_truncnorm', 'atkinson', 'gini', 'robinhood']

warnings.filterwarnings("ignore", category=DeprecationWarning)


def measure_hubness(n_tracks, output_file, metric, projection, dimensions, n_jobs, random):
    from skhubness import Hubness
    tracks = Track.get_all(limit=n_tracks, random=random)

    models = get_models()
    models_iter = models.get_combinations() if projection is None else models.get_offline_projections(projection)
    results = []
    for model in list(models_iter):
        for _dimensions in tqdm(range(2, dimensions+1), desc=str(model)):
            embeddings = model.get_embeddings(tracks, dimensions=slice(_dimensions))
            embeddings_stacked = np.vstack(embeddings)

            hub = Hubness(k=10, metric=metric, return_value='all', n_jobs=n_jobs)
            hub.fit(embeddings_stacked[:, :_dimensions])
            result = {key: value for key, value in hub.score().items() if key in RETURN_VALUES}
            result.update({
                'model': f'{model.dataset}-{model.architecture}',
                'layer': model.layer,
                'dimensions': _dimensions
            })
            results.append(result)

    results_df = pd.DataFrame(results)
    results_df.to_csv(output_file, float_format=FLOAT_FORMAT)


def visualize_hubness(input_file):
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(input_file, index_col=0, comment='#')

    for layer in ['embeddings', 'taggrams']:
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))

        df_layer = df[df.layer == layer]
        for return_value, ax in zip(PLOT_VALUES, axes.flatten()):
            sns.lineplot(ax=ax, data=df_layer, x='dimensions', y=return_value, style='model')
            ax.set_title(return_value)

        fig.savefig(f'data/hubness_{layer}.pdf')

    # px.line(df[df.layer == 'embeddings'], color='model', x='dimensions', y='gini', template='').show()


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
