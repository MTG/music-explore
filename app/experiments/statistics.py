import logging
from pathlib import Path
from typing import Iterable

import click
import numpy as np
import pandas as pd
from flask.cli import with_appcontext
from tqdm import tqdm

from app.database.base import Track
from app.database.metadata import Tag
from app.models import Model, get_models

FLOAT_FORMAT = '%.4f'
FILENAME_TAGS_STD = 'tags-std.csv'
FILENAME_TAGS_MEAN = 'tags-mean.csv'
FILENAME_ALL_MEAN_STD = 'all-mean-std.csv'


def _get_mean_and_std(model: Model, tracks: Iterable[Track]):
    embeddings = model.get_embeddings_from_file(tracks)
    embeddings_stacked = np.vstack(embeddings)
    return embeddings_stacked.mean(axis=0), embeddings_stacked.std(axis=0)


def save_if_not_exists(results, output_file):
    if output_file.exists():
        print(f'{output_file} already exists, skipping')
        return

    output_file.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(results)
    df.to_csv(output_file, float_format=FLOAT_FORMAT)


def measure_tag_spread(model: Model, output_dir, n_tags=None):
    results_mean = {}
    results_std = {}

    for tag in tqdm(Tag.get_all(limit=n_tags)):
        tracks = [track_metadata.track for track_metadata in tag.tracks_metadata]
        results_mean[tag.name], results_std[tag.name] = _get_mean_and_std(model, tracks)

    save_if_not_exists(results_mean, output_dir / FILENAME_TAGS_MEAN)
    save_if_not_exists(results_std, output_dir / FILENAME_TAGS_STD)


def measure_model_spread(model: Model, output_dir, n_tracks):
    mean, std = _get_mean_and_std(model, tqdm(Track.get_all(limit=n_tracks)))
    results = {'mean': mean, 'std': std}

    save_if_not_exists(results, output_dir / FILENAME_ALL_MEAN_STD)


@click.command('measure-tag-spread')
@click.argument('dataset')
@click.argument('architecture')
@click.argument('layer')
@click.argument('output_dir', type=click.Path())
@click.option('-n', '--n-tags', type=int)
@with_appcontext
def measure_tag_spread_command(dataset, architecture, layer, output_dir, n_tags):
    model = Model(get_models().data, dataset, architecture, layer, projection=None)
    measure_tag_spread(model, Path(output_dir), n_tags)


@click.command('measure-model-spread')
@click.argument('dataset')
@click.argument('architecture')
@click.argument('layer')
@click.argument('output_file', type=click.Path())
@click.option('-n', '--n-tracks', type=int)
@with_appcontext
def measure_model_spread_command(dataset, architecture, layer, output_dir, n_tracks):
    model = Model(get_models().data, dataset, architecture, layer, projection=None)
    measure_model_spread(model, Path(output_dir), n_tracks)


@click.command('measure-spread')
@click.argument('output_dir', type=click.Path())
@click.option('--n-tracks', type=int)
@click.option('--n-tags', type=int)
@with_appcontext
def measure_spread_command(output_dir, n_tracks, n_tags):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for model in get_models().get_all_offline():
        logging.info(f'Analyzing {model}..')
        measure_model_spread(model, output_dir / str(model), n_tracks)
        measure_tag_spread(model, output_dir / str(model), n_tags)
