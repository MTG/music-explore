from pathlib import Path
import logging

import pandas as pd
import click
from flask.cli import with_appcontext
import plotly.express as px

from app.models import Model, get_models


def read_spread(model: Model, input_dir):
    input_dir = Path(input_dir)
    df_all = pd.read_csv(input_dir / f'{model}-std.csv', index_col=0)
    df_tags = pd.read_csv(input_dir / f'{model}-tags.csv', index_col=0)
    # return df_tags
    return df_tags.div(df_all['all'], axis='index')


def plot_dimension_spread(model: Model, input_dir):
    df = read_spread(model, input_dir)
    kwargs = {}
    if model.layer == 'taggrams':
        kwargs['y'] = model.dataset_data['tags']
    fig = px.imshow(df, labels={'x': 'Tag', 'y': 'Dimension', 'color': 'Std'}, **kwargs)
    fig.show()


def synthesize_spread_metric(model: Model, input_dir):
    input_dir = Path(input_dir)
    df_std = pd.read_csv(index_col=0)


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
