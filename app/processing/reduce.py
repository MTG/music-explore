from pathlib import Path
from typing import List

from tqdm import tqdm
import numpy as np
from typing import Iterable
from sklearn.decomposition import PCA, IncrementalPCA
from sklearn.manifold import TSNE
import click
from flask.cli import with_appcontext
from flask import current_app

from app.utils import list_files, get_embeddings
from app.models import get_models


def reduce_pca(embeddings: Iterable[np.ndarray]):
    projection = PCA(random_state=0, copy=False)
    return reduce_generic(list(embeddings), projection)


def reduce_tsne(embeddings: Iterable[np.ndarray]):
    projection = TSNE(n_components=2, random_state=0, verbose=True)
    return reduce_generic(list(embeddings), projection)


def reduce_ipca(embeddings: Iterable[np.ndarray], batch_size=None):
    # TODO: finish implementation
    projection = IncrementalPCA(copy=False)
    raise NotImplementedError()


def reduce_generic(embeddings: List[np.ndarray], projection, n_input_dimensions=None):
    """Stacks embeddings into one matrix, performs dimensionality reduction and splits them back. Optionally
    preprocesses stacked embeddings"""

    embeddings_stacked = np.vstack(embeddings)
    lengths = list(map(len, embeddings))

    embeddings_reduced = projection.fit_transform(embeddings_stacked[:, :n_input_dimensions])

    return np.split(embeddings_reduced, np.cumsum(lengths)[:-1])


REDUCE = {
    'pca': reduce_pca,
    'tsne': reduce_tsne,
    'ipca': reduce_ipca
}


def reduce(input_dir, output_dir, projection: str, n_tracks=None, dry=False, force=False):
    embedding_files = list_files(input_dir, '*.npy')[:n_tracks]

    print(f'Loading embeddings in {input_dir}...')
    embeddings = get_embeddings(embedding_files)

    print(f'Applying {projection}...')
    try:
        embeddings_reduced = REDUCE[projection](embeddings)
    except KeyError:
        raise ValueError(f'Invalid projection_type: {projection}')

    print('Saving reduced...')
    if not dry:
        output_dir = Path(output_dir)
        for embedding_file, data in zip(tqdm(embedding_files), embeddings_reduced):
            relative_path = embedding_file.relative_to(input_dir)
            output_file = output_dir / relative_path
            if force or not output_file.exists():
                output_file.parent.mkdir(parents=True, exist_ok=True)
                np.save(output_file, data)

    print('Done!')


def reduce_all(n_tracks=None, dry=False, force=False):
    app = current_app
    data_dir = Path(app.config['DATA_DIR'])

    models = get_models()
    for model in models.get_offline_projections():
        print(f'Generating {model}')
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
@click.argument('projection', type=click.Choice(['pca', 'ipca', 'tsne'], case_sensitive=False))
@click.option('-n', '--n_tracks', type=int, help='only process limited amount of tracks')
@click.option('-d', '--dry', is_flag=True, help='simulate the run')
@click.option('-f', '--force', is_flag=True, help='force overwriting of embedding files')
def reduce_command(input_dir, output_dir, projection: str, n_tracks, dry, force):
    reduce(input_dir, output_dir, projection, n_tracks, dry, force)


@click.command('reduce-all')
@click.option('-n', '--n_tracks', type=int, help='only process limited amount of tracks')
@click.option('-d', '--dry', is_flag=True, help='simulate the run')
@click.option('-f', '--force', is_flag=True, help='force overwriting of embedding files')
def reduce_all_command(n_tracks, dry, force):
    reduce_all(n_tracks, dry, force)
