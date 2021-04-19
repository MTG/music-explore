import csv

import click
import requests
from flask import current_app
from flask.cli import with_appcontext
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from tqdm import tqdm

from app.database.base import Track, db, needs_committing
from app.database.metadata import Album, Artist, Tag, TrackMetadata

TAG_HYPHEN = '---'


def parse_id(value):
    return int(value.split('_')[1])


def load_jamendo_metadata(input_file):
    total_rows = sum(1 for _ in open(input_file)) - 1

    with open(input_file) as fp:
        reader = csv.reader(fp, delimiter='\t')
        next(reader, None)  # skip header

        session_size = 0
        for row in tqdm(reader, total=total_rows):  # TODO: investigate why performance slows down
            track_jamendo_id = parse_id(row[0])
            artist_id = parse_id(row[1])
            album_id = parse_id(row[2])
            path = row[3]
            raw_tags = row[5:]

            track = db.session.query(Track).filter(Track.path == path).first()
            if track is not None:
                if TrackMetadata.get_by_id(track.id) is None:
                    artist = Artist.get_by_id(artist_id)
                    if artist is None:
                        artist = Artist(id=artist_id)
                        db.session.add(artist)

                    album = Album.get_by_id(album_id)
                    if album is None:
                        album = Album(id=album_id, artist=artist)
                        db.session.add(artist)

                    track_metadata = TrackMetadata(track=track, streaming_id=str(track_jamendo_id),
                                                   album=album, artist=artist)
                    db.session.add(track_metadata)

                    for raw_tag in raw_tags:
                        # split genre---rock into group=genre and name=rock
                        tag_group, tag_name = raw_tag.split(TAG_HYPHEN)
                        tag = Tag.get_by_name_and_group(tag_name, tag_group)
                        if tag is None:
                            tag = Tag(name=tag_name, group=tag_group)
                            db.session.add(tag)

                        tag.tracks_metadata.append(track_metadata)

                    session_size += 1
                    if needs_committing(session_size):
                        db.session.commit()
                        session_size = 0

    db.session.commit()


def get_http_session():
    retry_strategy = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http_session = requests.Session()
    http_session.mount("https://", adapter)
    http_session.mount("http://", adapter)
    return http_session


def query_jamendo_metadata(db_model, jamendo_entity, batch_size, http_session=None):
    if http_session is None:
        http_session = get_http_session()

    url = f'https://api.jamendo.com/v3.0/{jamendo_entity}/'
    # we need '==' instead of 'is' for None comparison in sqlalchemy
    noname_rows = db.session.query(db_model).filter(db_model.name == None).all()  # noqa: E711
    for rows in tqdm([noname_rows[pos:pos + batch_size] for pos in range(0, len(noname_rows), batch_size)],
                     desc=jamendo_entity):

        if db_model == TrackMetadata:
            id_mapping = {row.streaming_id: row.id for row in rows}

            def map_id(_id):
                return id_mapping[_id]
            ids = set(id_mapping.keys())
        else:
            def map_id(_id):
                return _id
            ids = {row.id for row in rows}

        params = {
            'client_id': current_app.config['JAMENDO_CLIENT_ID'],
            'id[]': list(ids),
            'limit': batch_size
        }

        response = http_session.get(url, params=params)
        if response.status_code != 200:
            response.raise_for_status()

        response_json = response.json()
        if response_json['headers']['code'] != 0:
            raise RuntimeError(response_json['headers']['error_message'])

        mappings = []
        for result in response_json['results']:
            mappings.append({
                'id': map_id(result['id']),
                'name': result['name']
            })
            ids.remove(result['id'])

        for missed_id in ids:
            mappings.append({
                'id': map_id(missed_id),
                'name': f'Deleted ({missed_id})'
            })

        db.session.bulk_update_mappings(db_model, mappings)
        db.session.commit()


def query_all_jamendo_metadata(batch_size):
    http_session = get_http_session()
    query_jamendo_metadata(Artist, 'artists', batch_size, http_session)
    query_jamendo_metadata(Album, 'albums', batch_size, http_session)
    query_jamendo_metadata(TrackMetadata, 'tracks', batch_size, http_session)


@click.command('load-jamendo-metadata')
@click.argument('input_file', type=click.Path(exists=True))
@with_appcontext
def load_jamendo_metadata_command(input_file):
    load_jamendo_metadata(input_file)


@click.command('query-jamendo-metadata')
@click.option('-b', '--batch-size', type=int, default=None)
@with_appcontext
def query_jamendo_metadata_command(batch_size):
    if batch_size is None:
        batch_size = current_app.config['JAMENDO_BATCH_SIZE']
    query_all_jamendo_metadata(batch_size)
