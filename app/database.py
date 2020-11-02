from pathlib import Path
from typing import List
import logging
from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import click
from flask import current_app
from flask.cli import with_appcontext
import numpy as np
from tqdm import tqdm


db = SQLAlchemy()


class CommonMixin:
    """
    Has primary key id, and methods get_by_id and get_all
    """
    id = Column(Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, _id):
        return db.session.query(cls).filter(cls.id == _id).first()

    @classmethod
    def get_all(cls):
        return db.session.query(cls)


class Track(CommonMixin, db.Model):
    __tablename__ = 'track'

    segmentations = relationship('Segmentation', back_populates='track')
    path = Column(String, index=True, unique=True)

    track_metadata = relationship('TrackMetadata', uselist=False, back_populates='track')

    def __repr__(self):
        return f'<Track({self.id}, path={self.path})>'

    # segmentations

    def has_segmentation(self, length):
        return self.get_segmentation(length).first() is not None

    def get_segmentation(self, length):
        return db.session.query(Segmentation).filter_by(id=self.id, length=length)

    # embeddings without annoy

    def get_embeddings_filename(self) -> Path:
        return Path(self.path).with_suffix('.npy')

    def get_embeddings_from_file(self, embeddings_dir) -> np.ndarray:
        path = Path(embeddings_dir) / self.get_embeddings_filename()
        return np.load(str(path))

    @staticmethod
    def get_all_embeddings_from_files(embedding_dir) -> List[np.ndarray]:
        return [track.get_embeddings_from_file(embedding_dir) for track in tqdm(Track.get_all())]

    @property  # TODO: replace with metadata streaming_id
    def jamendo_id(self):
        return Path(self.path).stem

    @staticmethod
    def get_by_path(path):
        return db.session.query(Track).filter(Track.path == path).first()


@dataclass()
class Segment:
    id: int
    length: int
    position: int
    track_id: int

    @staticmethod
    def _str(time):
        """Transforms float into decimal format"""
        precision = current_app.config['SEGMENT_PRECISION']
        return f'{time:.{precision}f}'

    def get_timestamps(self):
        """Returns start and end timestamps in seconds"""
        return self.position * self.length / 1000, (self.position + 1) * self.length / 1000

    def get_time(self):
        start, end = self.get_timestamps()
        return f'{self._str(start)}:{self._str(end)}'

    def get_url_suffix(self):
        start, end = self.get_timestamps()
        return f'#t={self._str(start)},{self._str(end)}'


class Segmentation(CommonMixin, db.Model):
    __tablename__ = 'segmentation'
    id = Column(Integer, ForeignKey('track.id'), primary_key=True)
    track = relationship('Track', back_populates='segmentations')
    length = Column(Integer, primary_key=True)  # in ms
    start_id = Column(Integer, index=True)
    stop_id = Column(Integer, index=True)

    def __repr__(self):
        return f'<Segmentation({self.start_id}:{self.stop_id}, track={self.id}, length={self.length}>'

    def get_segments(self):
        return [Segment(segment_id, self.length, segment_id - self.start_id, self.id)
                for segment_id in range(self.start_id, self.stop_id)]


track_metadata_tag_table = Table('track_metadata_tag', db.Model.metadata,
                                 Column('tag_id', Integer, ForeignKey('tag.id')),
                                 Column('track_id', Integer, ForeignKey('track_metadata.id'))
                                 )


class TrackMetadata(CommonMixin, db.Model):
    __tablename__ = 'track_metadata'
    id = Column(Integer, ForeignKey('track.id'), primary_key=True)
    track = relationship('Track', back_populates='track_metadata')
    streaming_id = Column(String, unique=True)
    name = Column(String)

    artist_id = Column(Integer, ForeignKey('artist.id'))
    artist = relationship('Artist', back_populates='tracks_metadata')

    album_id = Column(Integer, ForeignKey('album.id'))
    album = relationship('Album', back_populates='tracks_metadata')

    tags = relationship('Tag', secondary=track_metadata_tag_table, back_populates='tracks_metadata')

    def __repr__(self):
        return f'<TrackMetadata({self.id}, jamendo:{self.streaming_id})>'


class Artist(CommonMixin, db.Model):
    __tablename__ = 'artist'
    name = Column(String)

    tracks_metadata = relationship('TrackMetadata', back_populates='artist')

    albums = relationship('Album', back_populates='artist')


class Album(CommonMixin, db.Model):
    __tablename__ = 'album'
    name = Column(String)

    tracks_metadata = relationship('TrackMetadata', back_populates='album')

    artist_id = Column(Integer, ForeignKey('artist.id'))
    artist = relationship('Artist', back_populates='albums')


class Tag(CommonMixin, db.Model):
    __tablename__ = 'tag'
    name = Column(String, index=True)
    group = Column(String, index=True)

    tracks_metadata = relationship('TrackMetadata', secondary=track_metadata_tag_table, back_populates='tags')


@click.command('init-db')
@with_appcontext
def init_db_command():
    db.create_all()
    logging.info('Created all tables')


def init_app(app):
    db.init_app(app)
    app.cli.add_command(init_db_command)
