from pathlib import Path
from typing import List
import logging

from sqlalchemy import Column, Integer, String, ForeignKey, exists
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import click
from flask.cli import with_appcontext
import numpy as np
from tqdm import tqdm


db = SQLAlchemy()


class Track(db.Model):
    __tablename__ = 'track'
    id = Column(Integer, primary_key=True)
    segments = relationship('Segment', back_populates='track')
    path = Column(String, index=True, unique=True)

    def _segments_query(self, length):
        return db.session.query(Segment).filter_by(track_id=self.id, length=length)

    def has_segments(self, length):
        # TODO: make it more elegant if possible
        return self._segments_query(length).first() is not None

    def get_segments(self, length):
        return self._segments_query(length).all()

    def get_segment(self, length, position):
        db.session.query(Segment).filter_by(track_id=self.id, length=length, position=position).first()

    def get_embeddings_filename(self) -> Path:
        return Path(self.path).with_suffix('.npy')

    def get_embeddings_from_file(self, embeddings_dir) -> np.ndarray:
        path = Path(embeddings_dir) / self.get_embeddings_filename()
        return np.load(str(path))

    @staticmethod
    def get_all_embeddings_from_files(embedding_dir) -> List[np.ndarray]:
        return [track.get_embeddings_from_file(embedding_dir) for track in tqdm(Track.get_all())]

    @staticmethod
    def get_all():
        return db.session.query(Track).all()


class Segment(db.Model):
    __tablename__ = 'segment'
    id = Column(Integer, primary_key=True)
    length = Column(Integer, primary_key=True)  # in ms

    track_id = Column(Integer, ForeignKey('track.id'))
    track = relationship('Track', back_populates='segments')
    position = Column(Integer)
    PRECISION = 3

    def __repr__(self):
        return f'{self.track_id}:{self.get_time()}'

    def get_time(self):
        start, stop = self.get_timestamps()
        return f'{start:.{self.PRECISION}}:{stop:.{self.PRECISION}}'

    def get_timestamps(self):
        """Returns start and end timestamps in seconds"""
        return self.position * self.length / 1000, (self.position + 1) * self.length / 1000


@click.command('init-db')
@with_appcontext
def init_db_command():
    db.create_all()
    logging.info('Created all tables')


def init_app(app):
    db.init_app(app)
    app.cli.add_command(init_db_command)
