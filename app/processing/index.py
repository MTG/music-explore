from pathlib import Path

from annoy import AnnoyIndex
import click
from flask.cli import with_appcontext
from flask import current_app

from app.utils import list_files, get_embeddings
from app.database import Segment, Track, db
from app.models import get_models


def build_index(input_dir, index_file, n_dimensions, db_session, segment_length, n_trees=16, n_tracks=None, dry=False,
                force=False):
    # TODO: incorporate dry and force flags into database operations
    last_index = 0
    embeddings_index = AnnoyIndex(n_dimensions, 'euclidean')

    embedding_files = list_files(input_dir, '*.npy')[:n_tracks]

    print(f'Loading embeddings in {input_dir}...')
    for embeddings, embedding_file in zip(get_embeddings(embedding_files, n_dimensions), embedding_files):
        path = str(embedding_file.relative_to(input_dir))
        track = db_session.query(Track).filter_by(path=path).first()
        if track is None:
            track = Track(path=path)
            db_session.add(track)
            has_segments = False
        else:
            has_segments = track.has_segments(db_session, segment_length)

        for i, embedding in enumerate(embeddings):
            segment_id = last_index + i
            embeddings_index.add_item(segment_id, embedding)  # annoy
            if not has_segments:
                db_session.add(Segment(id=segment_id, length=segment_length, track=track, position=i))

        last_index += len(embeddings)

    print('Updating database...')
    db_session.commit()

    print('Building index...')
    embeddings_index.build(n_trees, n_jobs=-1)

    if not dry:
        if Path(index_file).exists():
            if force:
                print(f'Overwriting {index_file} with new index...')
                embeddings_index.save(index_file)
            else:
                print(f'Index {index_file} already exists, if you want to overwrite it, please use --force')
        else:
            print(f'Saving index to {index_file}...')
            embeddings_index.save(index_file)


def build_all_indices(n_trees=16, n_tracks=None, dry=False, force=False):
    app = current_app
    data_dir = Path(app.config['DATA_DIR'])
    index_dir = Path(app.config['INDEX_DIR'])

    models = get_models()
    for model in models.get_all_offline():
        build_index(
            data_dir / str(model),
            index_dir / f'{model}.ann',
            model.layer_data['size'],
            db.session,
            model.model_data['segment-length'],
            n_trees, n_tracks, dry, force
        )


# Entry points

@click.command('build-index')
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('index_file', type=click.Path())
@click.argument('n_dimensions', type=int)
@click.argument('segment_length', type=int)
@click.option('-t', '--n_trees', type=int, default=16, help='number of trees for the annoy index')
@click.option('-n', '--n_tracks', type=int, help='only process limited amount of tracks')
@click.option('-d', '--dry', is_flag=True, help='simulate the run')
@click.option('-f', '--force', is_flag=True, help='overwrite annoy index and database entries if they exist')
@with_appcontext
def build_index_command(input_dir, index_file, n_dimensions, segment_length, n_trees, n_tracks, dry, force):
    """Go through embeddings in INPUT_DIR and create a new annoy index INDEX_FILE from them with N_DIMENSIONS.
    At the same time add all the tracks and segments to database if they don't exist yet with the SEGMENT_LENGTH"""
    build_index(input_dir, index_file, n_dimensions, db.session, segment_length, n_trees, n_tracks, dry, force)


@click.command('build-all-indices')
@click.option('-t', '--n_trees', type=int, default=16, help='number of trees for the annoy index')
@click.option('-n', '--n_tracks', type=int, help='only process limited amount of tracks')
@click.option('-d', '--dry', is_flag=True, help='simulate the run')
@click.option('-f', '--force', is_flag=True, help='overwrite annoy index and database entries if they exist')
def build_all_indices_command(n_trees, n_tracks, dry, force):
    build_all_indices(n_trees, n_tracks, dry, force)
