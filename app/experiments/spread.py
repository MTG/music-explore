from typing import Iterable
from pathlib import Path
import logging

import numpy as np
from tqdm import tqdm
import pandas as pd
import click
from flask.cli import with_appcontext

from app.database import Tag, Track
from app.models import Model, get_models

FLOAT_FORMAT = '%.4f'


def _get_std(model, tracks: Iterable[Track]):
    embeddings = model.get_embeddings_from_file(tracks)
    embeddings_stacked = np.vstack(embeddings)
    return embeddings_stacked.std(axis=0)


def measure_tag_spread(model: Model, output_file, n_tags=None):
    if output_file.exists():
        print(f'{output_file} already exists, skipping')
        return

    results = {}

    for tag in tqdm(Tag.get_all(limit=n_tags)):
        tracks = [track_metadata.track for track_metadata in tag.tracks_metadata]
        results[tag.name] = _get_std(model, tracks)

    df = pd.DataFrame(results)
    df.to_csv(output_file, float_format=FLOAT_FORMAT)


def measure_model_spread(model, output_file, n_tracks):
    if output_file.exists():
        print(f'{output_file} already exists, skipping')
        return

    results = {'all': _get_std(model, tqdm(Track.get_all(limit=n_tracks)))}

    df = pd.DataFrame(results)
    df.to_csv(output_file, float_format=FLOAT_FORMAT)


@click.command('measure-tag-spread')
@click.argument('dataset')
@click.argument('architecture')
@click.argument('layer')
@click.argument('output_file', type=click.Path())
@click.option('-n', '--n-tags', type=int)
@with_appcontext
def measure_tag_spread_command(dataset, architecture, layer, output_file, n_tags):
    model = Model(get_models().data, dataset, architecture, layer, projection=None)
    measure_tag_spread(model, output_file, n_tags)


@click.command('measure-model-spread')
@click.argument('dataset')
@click.argument('architecture')
@click.argument('layer')
@click.argument('output_file', type=click.Path())
@click.option('-n', '--n-tracks', type=int)
@with_appcontext
def measure_model_spread_command(dataset, architecture, layer, output_file, n_tracks):
    model = Model(get_models().data, dataset, architecture, layer, projection=None)
    measure_model_spread(model, output_file, n_tracks)


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
        measure_model_spread(model, output_dir / f'{model}-std.csv', n_tracks)
        measure_tag_spread(model, output_dir / f'{model}-tags.csv', n_tags)
