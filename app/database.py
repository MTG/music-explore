from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import click
import numpy as np
from flask import current_app
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String, Table, and_, or_
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

db = SQLAlchemy()


def needs_committing(session_size):
    return session_size >= current_app.config['DB_COMMIT_BATCH_SIZE']


class CommonMixin:
    """
    Has primary key id, and methods get_by_id and get_all
    """
    id = Column(Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, _id):
        return db.session.query(cls).filter(cls.id == _id).first()

    @classmethod
    def get_all(cls, limit=None, random=False):
        query = db.session.query(cls)

        if random:
            query = query.order_by(func.random())

        if limit is not None:
            query = query.limit(limit)
        return query.all()  # mostly used with tqdm, so it's nice to have len from .all()


class Track(CommonMixin, db.Model):
    __tablename__ = 'track'

    segmentations = relationship('Segmentation', back_populates='track')
    path = Column(String, index=True, unique=True)

    track_metadata = relationship('TrackMetadata', uselist=False, back_populates='track')

    def __repr__(self):
        return f'Track(id={self.id}, path={self.path})'

    # segmentations

    def has_segmentation(self, length):
        return self._get_segmentation(length) is not None

    def _get_segmentation(self, length):
        return db.session.query(Segmentation).filter_by(id=self.id, length=length).first()

    def get_segments(self, length):
        return self._get_segmentation(length).get_segments()

    # embeddings without annoy

    def get_embeddings_filename(self) -> Path:
        return Path(self.path).with_suffix('.npy')

    def get_embeddings_from_file(self, embeddings_dir) -> np.ndarray:
        path = Path(embeddings_dir) / self.get_embeddings_filename()
        return np.load(str(path))

    @property  # TODO: replace with metadata streaming_id
    def jamendo_id(self):
        return Path(self.path).stem

    @staticmethod
    def get_by_path(path):
        return db.session.query(Track).filter(Track.path == path).first()

    @property
    def full_id(self):
        return f'track/{self.id}'


@dataclass
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

    @staticmethod
    def _to_mm_ss(t):
        return f'{int(t / 60)}:{int(t % 60):02}'

    def get_timestamps(self):
        """Returns start and end timestamps in seconds"""
        return self.position * self.length / 1000, (self.position + 1) * self.length / 1000

    def get_time(self):
        start, end = self.get_timestamps()
        return f'{self._to_mm_ss(start)}~{self._to_mm_ss(end)}'

    def get_url_suffix(self):
        start, end = self.get_timestamps()
        return f'#t={self._str(start)},{self._str(end)}'

    @staticmethod
    def get_by_id(segment_length, segment_id):
        return Segmentation.get_by_segment_id(segment_length, segment_id).get_segment(segment_id)

    @property
    def track(self):
        return Track.get_by_id(self.track_id)

    def to_text(self):
        return f'{self.track.track_metadata.to_text()} ({self.get_time()})'

    @property
    def full_id(self):
        return f'segment/{self.length}/{self.id}'


class Segmentation(CommonMixin, db.Model):
    __tablename__ = 'segmentation'
    id = Column(Integer, ForeignKey('track.id'), primary_key=True)
    track = relationship('Track', back_populates='segmentations')
    length = Column(Integer, primary_key=True)  # in ms

    # segment_ids
    start_id = Column(Integer, index=True)
    stop_id = Column(Integer, index=True)

    def __repr__(self):
        return f'<Segmentation({self.start_id}:{self.stop_id}, track={self.id}, length={self.length}>'

    def get_segment(self, segment_id):
        return Segment(segment_id, self.length, segment_id - self.start_id, self.id)

    def get_segments(self):
        return [self.get_segment(segment_id) for segment_id in range(self.start_id, self.stop_id)]

    @staticmethod
    def get_by_segment_id(segment_length, segment_id):
        return db.session.query(Segmentation).filter(and_(Segmentation.length == segment_length,
                                                          Segmentation.start_id <= segment_id,
                                                          Segmentation.stop_id > segment_id)).first()

    @staticmethod
    def get_total_segments(segment_length):
        return db.session.query(func.max(Segmentation.stop_id)).filter(
            Segmentation.length == segment_length).first()[0]


track_metadata_tag_table = Table('track_metadata_tag', db.Model.metadata,
                                 Column('tag_id', Integer, ForeignKey('tag.id')),
                                 Column('track_id', Integer, ForeignKey('track_metadata.id'))
                                 )


class NameMixin(CommonMixin):
    name = Column(String, index=True)

    @classmethod
    def get_by_name(cls, name):
        return db.session.query(cls).filter_by(name=name).first()

    def __lt__(self, other):
        return (self.name is None, self.name) < (other.name is None, other.name)


class TrackMetadata(NameMixin, db.Model):
    __tablename__ = 'track_metadata'
    id = Column(Integer, ForeignKey('track.id'), primary_key=True)
    track = relationship('Track', back_populates='track_metadata')
    streaming_id = Column(String, unique=True)

    artist_id = Column(Integer, ForeignKey('artist.id'))
    artist = relationship('Artist', back_populates='tracks_metadata')

    album_id = Column(Integer, ForeignKey('album.id'))
    album = relationship('Album', back_populates='tracks_metadata')

    tags = relationship('Tag', secondary=track_metadata_tag_table, back_populates='tracks_metadata')

    def __repr__(self):
        return f'TrackMetadata(id={self.id}, streaming_id={self.streaming_id})'

    def to_text(self):
        return f'{self.artist.name} - {self.name}'

    @staticmethod
    def get_by_tags_and_artists(tag_ids, artist_ids):
        return db.session.query(TrackMetadata).join(Tag.tracks_metadata).filter(or_(
            TrackMetadata.artist_id.in_(artist_ids),
            Tag.id.in_(tag_ids)
        )).all()


class Artist(NameMixin, db.Model):
    __tablename__ = 'artist'

    tracks_metadata = relationship('TrackMetadata', back_populates='artist')

    albums = relationship('Album', back_populates='artist')


class Album(NameMixin, db.Model):
    __tablename__ = 'album'

    tracks_metadata = relationship('TrackMetadata', back_populates='album')

    artist_id = Column(Integer, ForeignKey('artist.id'))
    artist = relationship('Artist', back_populates='albums')


class Tag(NameMixin, db.Model):
    __tablename__ = 'tag'
    group = Column(String, index=True)

    tracks_metadata = relationship('TrackMetadata', secondary=track_metadata_tag_table, back_populates='tags')

    @staticmethod
    def get_by_name_and_group(tag_name, tag_group):
        return db.session.query(Tag).filter(Tag.name == tag_name).filter(Tag.group == tag_group).first()


@click.command('init-db')
@with_appcontext
def init_db_command():
    db.create_all()
    logging.info('Created all tables')


def init_app(app):
    db.init_app(app)
    app.cli.add_command(init_db_command)
