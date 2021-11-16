# import logging
import logging
from pathlib import Path

import click
from flask import current_app
from flask.cli import with_appcontext
from tqdm import tqdm

from app.database.base import Track, db, needs_committing
from app.database.metadata import Album, Artist, Tag, TrackMetadata


def load_id3_metadata(n_tracks=None):
    from tinytag import TinyTag
    from tinytag.tinytag import TinyTagException

    audio_dir = Path(current_app.config['AUDIO_DIR'])

    session_size = 0
    for track in tqdm(Track.get_all(limit=n_tracks)):
        path = audio_dir / track.path
        try:
            metadata = TinyTag.get(path)
        except TinyTagException:
            logging.error(f'Cannot read ID3 tags from {path}')

        if TrackMetadata.get_by_id(track.id) is None:
            track_name = metadata.title

            artist_name = metadata.artist
            # logging.debug(artist_name)
            artist = Artist.get_by_name(artist_name)
            if artist is None:
                artist = Artist(name=artist_name)
                db.session.add(artist)

            album_name = metadata.album
            # logging.debug(album_name)
            album = Album.get_by_name(album_name)
            if album is None:
                album = Album(name=album_name, artist=artist)
                db.session.add(album)

            track_metadata = TrackMetadata(track=track, name=track_name, album=album, artist=artist)
            db.session.add(track_metadata)

            genre = metadata.genre
            # logging.debug(genre)
            if genre:
                tag = Tag.get_by_name_and_group(genre, 'genre')
                if tag is None:
                    tag = Tag(name=genre, group='genre')
                    db.session.add(tag)
                tag.tracks_metadata.append(track_metadata)

            session_size += 1
            if needs_committing(session_size):
                db.session.commit()
                session_size = 0

    db.session.commit()


@click.command('load-id3-metadata')
@click.option('-n', '--n-tracks', type=int)
@with_appcontext
def load_id3_metadata_command(n_tracks):
    load_id3_metadata(n_tracks)
