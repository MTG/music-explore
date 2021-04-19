from pathlib import Path
from typing import Optional

import click
import numpy as np
from flask import current_app
from flask.cli import with_appcontext
from tqdm import tqdm

from app.database.base import Track
from app.models import Model, get_models


def aggregate(model: Model, output_file: Path, n_tracks: Optional[int] = None):
    tracks = tqdm(Track.get_all(limit=n_tracks), desc=str(model))
    embeddings = model.get_embeddings_from_file(tracks)
    embeddings = np.vstack(embeddings)
    embeddings = embeddings.astype(np.float16)
    np.save(output_file, embeddings)


@click.command('embeddings-to-float16')
@with_appcontext
def embeddings_to_float16():
    embeddings_dir = Path(current_app.config['DATA_DIR'])
    for embeddings_file in tqdm(sorted(embeddings_dir.rglob('*.npy'))):
        np.save(embeddings_file, np.load(embeddings_file).astype(np.float16))


@click.command('aggregate')
@click.argument('dataset', type=str)
@click.argument('architecture', type=str)
@click.argument('layer', type=str)
@click.argument('output_file', type=click.Path())
@click.option('-p', '--projection', type=str)
@click.option('-n', '--n-tracks', type=int, help='only process limited amount of tracks')
@with_appcontext
def aggregate_command(dataset, architecture, layer, output_file, projection, n_tracks):
    model = Model(get_models(), dataset, architecture, layer, projection)
    aggregate(model, Path(output_file), n_tracks)


@click.command('aggregate-all')
@click.option('-n', '--n-tracks', type=int, help='only process limited amount of tracks')
@with_appcontext
def aggregate_all_command(n_tracks):
    aggrdata_dir = Path(current_app.config['AGGRDATA_DIR'])
    aggrdata_dir.mkdir(parents=True, exist_ok=True)

    models = get_models()
    for model in models.get_all_offline():
        aggregate(model, aggrdata_dir / str(model), n_tracks)
