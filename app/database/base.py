from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import click
import numpy as np
from flask import current_app
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Integer, String, and_, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


def needs_committing(session_size):
    return session_size >= current_app.config['DB_COMMIT_BATCH_SIZE']


class CommonMixin:
    """
    Has primary key id, and methods get_by_id and get_all
    """

    id: Mapped[int] = mapped_column(primary_key=True)

    @classmethod
    def get_by_id(cls, _id):
        if _id is None:
            return None
        return db.session.get(cls, _id)

    @classmethod
    def get_by_ids(cls, _ids: list):
        if not _ids:
            return []
        stmt = select(cls).where(cls.id.in_(_ids))
        return list(db.session.execute(stmt).scalars())

    @classmethod
    def get_all(cls, limit=None, random=False):
        stmt = select(cls)

        if random:
            stmt = stmt.order_by(func.random())

        if limit is not None:
            stmt = stmt.limit(limit)
        return list(db.session.execute(stmt).scalars())  # mostly used with tqdm, so it's nice to have len from .all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class Track(CommonMixin, db.Model):
    __tablename__ = 'track'

    segmentations: Mapped[list['Segmentation']] = relationship('Segmentation', back_populates='track')
    path: Mapped[str] = mapped_column(String, index=True, unique=True)

    track_metadata: Mapped['TrackMetadata | None'] = relationship(  # noqa: F821
        'TrackMetadata', uselist=False, back_populates='track'
    )

    def __repr__(self):
        return f'Track(id={self.id}, path={self.path})'

    # segmentations

    def has_segmentation(self, length):
        return self._get_segmentation(length) is not None

    def _get_segmentation(self, length):
        stmt = select(Segmentation).where(Segmentation.id == self.id, Segmentation.length == length)
        return db.session.execute(stmt).scalar_one_or_none()

    def get_segments(self, length, sparse_factor=1):
        return self._get_segmentation(length).get_segments(sparse_factor)

    # embeddings without annoy

    def get_embeddings_filename(self) -> Path:
        return Path(self.path).with_suffix('.npy')

    def get_embeddings_from_file(self, embeddings_dir) -> np.ndarray:
        path = Path(embeddings_dir) / self.get_embeddings_filename()
        return np.load(str(path)).astype(np.float16)

    def get_aggrdata_slice(self, length, sparse_factor) -> slice:
        s = self._get_segmentation(length)
        return s.get_slice(sparse_factor)

    @property  # TODO: replace with metadata streaming_id
    def jamendo_id(self):
        return Path(self.path).stem

    @staticmethod
    def get_by_path(path):
        stmt = select(Track).where(Track.path == path)
        return db.session.execute(stmt).scalar_one_or_none()

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
    def get_by_id(segment_length: int, segment_id: int):
        return Segmentation.get_by_segment_id(segment_length, segment_id).get_segment(segment_id)

    @property
    def track(self):
        return Track.get_by_id(self.track_id)

    def to_text(self):
        return self.get_time()

    @property
    def full_id(self):
        return f'segment/{self.length}/{self.id}'


class Segmentation(CommonMixin, db.Model):
    __tablename__ = 'segmentation'
    id: Mapped[int] = mapped_column(ForeignKey('track.id'), primary_key=True)
    track: Mapped['Track'] = relationship('Track', back_populates='segmentations')
    length: Mapped[int] = mapped_column(Integer, primary_key=True)  # in ms

    # segment_ids
    start_id: Mapped[int] = mapped_column(Integer, index=True)
    stop_id: Mapped[int] = mapped_column(Integer, index=True)

    def __repr__(self):
        return f'<Segmentation({self.start_id}:{self.stop_id}, track={self.id}, length={self.length}>'

    def get_segment(self, segment_id):
        return Segment(segment_id, self.length, segment_id - self.start_id, self.id)

    def get_segments(self, sparse_factor):
        return [self.get_segment(segment_id) for segment_id in range(self.start_id, self.stop_id, sparse_factor)]

    @staticmethod
    def get_by_segment_id(segment_length: int, segment_id: int):
        stmt = select(Segmentation).where(
            and_(
                Segmentation.length == segment_length,
                Segmentation.start_id <= segment_id,
                Segmentation.stop_id > segment_id,
            )
        )
        return db.session.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_total_segments(segment_length):
        stmt = select(func.max(Segmentation.stop_id)).where(Segmentation.length == segment_length)
        result = db.session.execute(stmt).scalar_one_or_none()
        return result or 0

    def get_slice(self, sparse_factor) -> slice:
        return slice(self.start_id, self.stop_id, sparse_factor)


@click.command('init-db')
@with_appcontext
def init_db_command():
    db.create_all()
    logging.info('Created all tables')
