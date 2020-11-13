from pathlib import Path
import logging

from annoy import AnnoyIndex
import click
from flask.cli import with_appcontext
from flask import current_app
from tqdm import tqdm

from app.database import Segmentation, Track, db, needs_committing
from app.models import get_models


def index_embeddings(input_dir, index_file, n_dimensions, segment_length, n_trees=16, n_tracks=None, dry=False, force=False):
    embeddings_index = AnnoyIndex(n_dimensions, current_app.config['ANNOY_DISTANCE'])
    index_file = Path(index_file)

    if index_file.exists() and not force:
        print(f'Index {index_file} already exists, skipping')
        return

    current_index = 0
    session_size = 0

    logging.info(f'Loading embeddings in {input_dir}...')
    for track in tqdm(Track.get_all(limit=n_tracks)):
        embeddings = track.get_embeddings_from_file(input_dir)
        total_segments = len(embeddings)

        for position, embedding in enumerate(embeddings):
            embeddings_index.add_item(current_index + position, embedding)  # annoy

        if not track.has_segmentation(segment_length):
            db.session.add(Segmentation(track=track, length=segment_length, start_id=current_index,
                                        stop_id=current_index + total_segments))
            session_size += 1

        if not dry and needs_committing(session_size):
            db.session.commit()
            session_size = 0

        current_index += total_segments

    if not dry:
        db.session.commit()  # commit remaining tracks in session

    logging.info('Building index...')
    embeddings_index.build(n_trees, n_jobs=-1)

    if not dry:
        index_file.parent.mkdir(parents=True, exist_ok=True)
        embeddings_index.save(str(index_file))

    logging.info('Done!')


def index_all_embeddings(n_trees=16, n_tracks=None, dry=False, force=False):
    app = current_app
    data_dir = Path(app.config['DATA_DIR'])

    models = get_models()
    for model in models.get_all_offline():
        index_embeddings(
            data_dir / str(model),
            model.index_file,
            model.n_dimensions,
            model.architecture_data['segment-length'],
            n_trees, n_tracks, dry, force
        )


# Entry points

@click.command('index-embeddings')
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('index_file', type=click.Path())
@click.argument('n_dimensions', type=int)
@click.argument('segment_length', type=int)
@click.option('-t', '--n-trees', type=int, default=16, help='number of trees for the annoy index')
@click.option('-n', '--n-tracks', type=int, help='only process limited amount of tracks')
@click.option('-d', '--dry', is_flag=True, help='simulate the run')
@click.option('-f', '--force', is_flag=True, help='overwrite annoy index and database entries if they exist')
@with_appcontext
def index_embeddings_command(input_dir, index_file, n_dimensions, segment_length, n_trees, n_tracks, dry, force):
    """Go through embeddings in INPUT_DIR and create a new annoy index INDEX_FILE from them with N_DIMENSIONS.
    At the same time add all the tracks and segments to database if they don't exist yet with the SEGMENT_LENGTH"""
    index_embeddings(input_dir, index_file, n_dimensions, segment_length, n_trees, n_tracks, dry, force)


@click.command('index-all-embeddings')
@click.option('-t', '--n-trees', type=int, default=16, help='number of trees for the annoy index')
@click.option('-n', '--n-tracks', type=int, help='only process limited amount of tracks')
@click.option('-d', '--dry', is_flag=True, help='simulate the run')
@click.option('-f', '--force', is_flag=True, help='overwrite annoy index and database entries if they exist')
@with_appcontext
def index_all_embeddings_command(n_trees, n_tracks, dry, force):
    index_all_embeddings(n_trees, n_tracks, dry, force)
