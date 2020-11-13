from pathlib import Path
import logging

import pandas as pd
import click
from flask.cli import with_appcontext
import plotly.express as px

from app.models import Model, get_models
from .statistics import FILENAME_ALL_MEAN_STD, FILENAME_TAGS_STD, FILENAME_TAGS_MEAN, FLOAT_FORMAT


def read_spread(model: Model, input_dir):
    input_dir = Path(input_dir) / str(model)
    df_all = pd.read_csv(input_dir / FILENAME_ALL_MEAN_STD, index_col=0)
    df_tags_mean = pd.read_csv(input_dir / FILENAME_TAGS_MEAN, index_col=0)
    df_tags_std = pd.read_csv(input_dir / FILENAME_TAGS_STD, index_col=0)
    return df_tags_mean.sub(df_all['mean'], axis='index').div(df_all['std'], axis='index'), \
           df_tags_std.div(df_all['std'], axis='index')


def plot_dimension_spread(model: Model, input_dir):
    df = read_spread(model, input_dir)
    kwargs = {}
    if model.layer == 'taggrams':
        kwargs['y'] = model.dataset_data['tags']
    fig = px.imshow(df,
                    labels={'x': 'Tag', 'y': 'Dimension', 'color': 'Std'},
                    color_continuous_midpoint=0,
                    color_continuous_scale='RdBu',
                    **kwargs)
    fig.show()


def synthesize_spread_metric(model: Model, input_dir):
    means, std = read_spread(model, input_dir)
    return std.mean().mean()


def plot_boxes(model: Model, input_dir):
    pass


@click.command('plot-dimension-spread')
@click.argument('dataset')
@click.argument('architecture')
@click.argument('layer')
@click.option('-p', '--projection')
@click.argument('input_dir', type=click.Path(exists=True))
@with_appcontext
def plot_dimension_spread_command(dataset, architecture, layer, projection, input_dir):
    model = Model(get_models().data, dataset, architecture, layer, projection=projection)
    plot_dimension_spread(model, input_dir)


@click.command('synthesize-all-spread-metrics')
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@with_appcontext
def synthesize_all_spread_metrics_command(input_dir, output_file):
    results = {}
    # only regular models, no projections
    for model in get_models().get_combinations():
        logging.info(f'Analyzing {model}..')
        results[str(model)] = synthesize_spread_metric(model, input_dir)

    df = pd.DataFrame.from_dict(results, orient='index', columns=['std'])
    df.to_csv(output_file, float_format=FLOAT_FORMAT)
