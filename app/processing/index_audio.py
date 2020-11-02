from pathlib import Path
import logging

from flask.cli import with_appcontext
from flask import current_app
import click
from tqdm import tqdm

from app.database import Track, db, needs_committing


def index_audio(input_dir, wildcard='*.mp3'):
    input_dir = Path(input_dir)
    audio_files = sorted(input_dir.rglob(wildcard))
    if len(audio_files) == 0:
        logging.error(f'No {wildcard} files found in {input_dir}')
        exit(1)

    session_size = 0
    logging.info(f'Indexing audio in {input_dir}')
    for audio_file in tqdm(audio_files):
        relative_path = str(audio_file.relative_to(input_dir))
        if Track.get_by_path(relative_path) is None:
            track = Track(path=str(relative_path))
            db.session.add(track)
            session_size += 1

            if needs_committing(session_size):
                db.session.commit()
                session_size = 0

    db.session.commit()
    logging.info('Done!')


def index_all_audio(wildcard='*.mp3'):
    audio_dir = Path(current_app.config['AUDIO_DIR'])
    index_audio(audio_dir, wildcard)


@click.command('index-audio')
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('-w', '--wildcard', default='*.mp3', help='wildcard that describes the audio files (e.g. *.mp3)')
@with_appcontext
def index_audio_command(input_dir, wildcard):
    index_audio(input_dir, wildcard)


@click.command('index-all-audio')
@click.option('-w', '--wildcard', default='*.mp3', help='wildcard that describes the audio files (e.g. *.mp3)')
@with_appcontext
def index_all_audio_command(wildcard):
    index_all_audio(wildcard)
