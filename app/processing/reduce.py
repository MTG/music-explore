import logging
from pathlib import Path
from typing import Iterable, List

import click
import numpy as np
from flask import current_app
from flask.cli import with_appcontext
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from tqdm import tqdm

from app.database.base import Track
from app.models import get_models


def reduce_generic(embeddings: List[np.ndarray], projection, n_input_dimensions=None, preprocess=None):
    """Stacks embeddings into one matrix, performs dimensionality reduction and splits them back. Optionally
    preprocesses stacked embeddings"""

    embeddings_stacked = np.vstack(embeddings)
    lengths = list(map(len, embeddings))

    if preprocess is not None:
        logging.info('Preprocessing...')
        embeddings_stacked = preprocess(embeddings_stacked)
        logging.info('Reducing...')

    embeddings_reduced = projection.fit_transform(embeddings_stacked[:, :n_input_dimensions])

    return np.split(embeddings_reduced, np.cumsum(lengths)[:-1])


def reduce_pca(embeddings: Iterable[np.ndarray]):
    projection = PCA(random_state=0, copy=False)
    return reduce_generic(list(embeddings), projection)


def reduce_tsne(embeddings: Iterable[np.ndarray]):
    projection = TSNE(n_components=2, random_state=0, verbose=True)
    # TODO: add n_input_dimension, as we don't need all pca as input to tsne
    return reduce_generic(list(embeddings), projection)


def reduce_umap(embeddings: Iterable[np.ndarray]):
    from umap import UMAP
    projection = UMAP(n_components=2, init='random', random_state=0)
    return reduce_generic(list(embeddings), projection)


def standardize(embeddings_stacked):
    return (embeddings_stacked - embeddings_stacked.mean(axis=0)) / embeddings_stacked.std(axis=0)


def reduce_std_pca(embeddings: Iterable[np.ndarray], batch_size=None):
    projection = PCA(random_state=0, copy=False)
    return reduce_generic(list(embeddings), projection, preprocess=standardize)


REDUCE = {
    'pca': reduce_pca,
    'tsne': reduce_tsne,
    'std-pca': reduce_std_pca
}


def reduce(input_dir, output_dir, projection: str, n_tracks=None, dry=False, force=False):
    try:
        reduce_func = REDUCE[projection]
    except KeyError:
        raise ValueError(f'Invalid projection_type: {projection}')

    embeddings = [track.get_embeddings_from_file(input_dir) for track in tqdm(Track.get_all(limit=n_tracks))]

    logging.info(f'Applying {projection}...')
    embeddings_reduced = reduce_func(embeddings)

    logging.info('Saving reduced...')
    if not dry:
        output_dir = Path(output_dir)
        for track, data in zip(tqdm(Track.get_all(limit=n_tracks)), embeddings_reduced):
            output_file = output_dir / track.get_embeddings_filename()
            if force or not output_file.exists():
                output_file.parent.mkdir(parents=True, exist_ok=True)
                np.save(output_file, data)

    logging.info('Done!')


def reduce_all(projection=None, n_tracks=None, dry=False, force=False):
    app = current_app
    data_dir = Path(app.config['DATA_DIR'])

    models = get_models()
    if projection is not None:
        projection_models = models.get_offline_projections(projection)
    else:
        projection_models = models.get_all_offline_projections()

    for model in projection_models:
        logging.info(f'Generating {model}')
        reduce(
            data_dir / str(model.without_projection()),
            data_dir / str(model),
            model.projection,
            n_tracks, dry, force
        )


# Entry points

@click.command('reduce')
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.argument('projection', type=click.Choice(REDUCE.keys(), case_sensitive=False))
@click.option('-n', '--n-tracks', type=int, help='only process limited amount of tracks')
@click.option('-d', '--dry', is_flag=True, help='simulate the run')
@click.option('-f', '--force', is_flag=True, help='force overwriting of embedding files')
@with_appcontext
def reduce_command(input_dir, output_dir, projection: str, n_tracks, dry, force):
    reduce(input_dir, output_dir, projection, n_tracks, dry, force)


@click.command('reduce-all')
@click.option('--projection', type=click.Choice(REDUCE.keys(), case_sensitive=False))
@click.option('-n', '--n-tracks', type=int, help='only process limited amount of tracks')
@click.option('-d', '--dry', is_flag=True, help='simulate the run')
@click.option('-f', '--force', is_flag=True, help='force overwriting of embedding files')
@with_appcontext
def reduce_all_command(projection, n_tracks, dry, force):
    reduce_all(projection, n_tracks, dry, force)
