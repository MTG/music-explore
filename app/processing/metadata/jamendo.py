import csv

from tqdm import tqdm
from flask.cli import with_appcontext
import click

from app.database import db, Track, TrackMetadata, Album, Artist, Tag, needs_committing


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

# def query_jamendo_api(batch_size):
#     for track_metadata in db.session.query(TrackMetadata).filter(TrackMetadata.name==None):


@click.command('load-jamendo-metadata')
@click.argument('input_file', type=click.Path(exists=True))
@with_appcontext
def load_jamendo_metadata_command(input_file):
    load_jamendo_metadata(input_file)


@click.command('query-jamendo-api')
@click.option('-b', '--batch-size', type=int, default=10)
@with_appcontext
def query_jamendo_api(batch_size):
    load_jamendo_metadata(batch_size)
