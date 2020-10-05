from pathlib import Path

from annoy import AnnoyIndex
import click
from flask.cli import with_appcontext

from app.utils import iterate_embeddings
from app.database import Segment, Track, db


def build_index(input_dir, index_file, n_dimensions, db_session, segment_length, n_trees=16, n_tracks=None, dry=False,
                force=False):
    # TODO: incorporate dry and force flags into database operations
    last_index = 0
    embeddings_index = AnnoyIndex(n_dimensions, 'euclidean')

    print(f'Processing embeddings in {input_dir}...')
    for embeddings, embedding_file in iterate_embeddings(input_dir, n_tracks, n_dimensions):
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


@click.command('build-index')
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('index_file', type=click.Path())
@click.argument('n_dimensions', type=int)
@click.argument('segment_length', type=int)
@click.option('-t', '--n_trees', type=int, default=16, help='number of trees for the annoy index')
@click.option('-n', '--n_tracks', type=int, help='only process this amount of tracks')
@click.option('-d', '--dry', is_flag=True, help='simulate the run, nothing gets actually updated or written')
@click.option('-f', '--force', is_flag=True, help='overwrite annoy index and database entries if they exist')
@with_appcontext
def build_index_command(input_dir, index_file, n_dimensions, segment_length, n_trees, n_tracks, dry, force):
    """Go through embeddings in INPUT_DIR adn create a new annoy index INDEX_FILE from them with N_DIMENSIONS.
    At the same time add all the tracks and segments to database if they don't exist yet with the SEGMENT_LENGTH"""
    build_index(input_dir, index_file, n_dimensions, db.session, segment_length, n_trees, n_tracks, dry, force)
