import logging
from glob import glob
from pathlib import Path

import click
from flask import current_app
from flask.cli import with_appcontext
from tqdm import tqdm

from app.database.base import Track, db, needs_committing


def index_audio(input_dir, wildcards):
    input_dir = Path(input_dir)
    audio_files = []
    for wildcard in wildcards:
        audio_files += glob(str(input_dir / '**' / wildcard), recursive=True)
    audio_files = sorted(audio_files)
    if len(audio_files) == 0:
        logging.error(f'No {wildcards} files found in {input_dir}')
        exit(1)
    logging.debug(f'Found {len(audio_files)} audio files')

    session_size = 0
    logging.info(f'Indexing audio in {input_dir}')
    for audio_file in tqdm(audio_files):
        relative_path = str(Path(audio_file).relative_to(input_dir))
        if Track.get_by_path(relative_path) is None:
            track = Track(path=str(relative_path))
            db.session.add(track)
            session_size += 1

            if needs_committing(session_size):
                db.session.commit()
                session_size = 0

    db.session.commit()
    logging.info('Done!')


def index_all_audio(wildcards):
    audio_dir = Path(current_app.config['AUDIO_DIR'])
    index_audio(audio_dir, wildcards)


@click.command('index-audio')
@click.argument('input_dir', type=click.Path(exists=True))
@click.option('-w', '--wildcards', default=['*.mp3', '*.flac'], multiple=True,
              help='wildcards that describes the audio files (e.g. *.mp3)')
@with_appcontext
def index_audio_command(input_dir, wildcards: tuple):
    index_audio(input_dir, wildcards)


@click.command('index-all-audio')
@click.option('-w', '--wildcards', default=['*.mp3', '*.flac'], multiple=True,
              help='wildcards that describes the audio files (e.g. *.mp3)')
@with_appcontext
def index_all_audio_command(wildcards):
    index_all_audio(wildcards)
