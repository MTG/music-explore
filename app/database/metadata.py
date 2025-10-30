from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, String, Table, or_, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import CommonMixin, db


class NameMixin(CommonMixin):
    name: Mapped[str | None] = mapped_column(String, index=True)

    @classmethod
    def get_by_name(cls, name):
        stmt = select(cls).where(cls.name == name)
        return db.session.execute(stmt).scalar_one_or_none()

    def __lt__(self, other):
        return (self.name is None, self.name) < (other.name is None, other.name)


track_metadata_tag_table = Table('track_metadata_tag', db.Model.metadata,
                                 Column('tag_id', Integer, ForeignKey('tag.id')),
                                 Column('track_id', Integer, ForeignKey('track_metadata.id'))
                                 )


class TrackMetadata(NameMixin, db.Model):
    __tablename__ = 'track_metadata'
    id: Mapped[int] = mapped_column(ForeignKey('track.id'), primary_key=True)
    track: Mapped['Track'] = relationship('Track', back_populates='track_metadata')
    streaming_id: Mapped[str | None] = mapped_column(String, unique=True)

    artist_id: Mapped[int | None] = mapped_column(ForeignKey('artist.id'))
    artist: Mapped['Artist | None'] = relationship('Artist', back_populates='tracks_metadata')

    album_id: Mapped[int | None] = mapped_column(ForeignKey('album.id'))
    album: Mapped['Album | None'] = relationship('Album', back_populates='tracks_metadata')

    tags: Mapped[list['Tag']] = relationship('Tag', secondary=track_metadata_tag_table,
                                             back_populates='tracks_metadata')

    def __repr__(self):
        return f'TrackMetadata(id={self.id}, streaming_id={self.streaming_id})'

    def to_text(self):
        return f'{self.artist.name} - {self.name}'

    def tags_to_text(self):
        return ', '.join([tag.name for tag in self.tags])

    @staticmethod
    def get_by_tags_and_artists(tag_ids, artist_ids):
        stmt = (
            select(TrackMetadata)
            .join(Tag.tracks_metadata)
            .where(
                or_(
                    TrackMetadata.artist_id.in_(artist_ids),
                    Tag.id.in_(tag_ids),
                )
            )
            .distinct()
        )
        return list(db.session.execute(stmt).scalars())


class Artist(NameMixin, db.Model):
    __tablename__ = 'artist'

    tracks_metadata: Mapped[list['TrackMetadata']] = relationship('TrackMetadata', back_populates='artist')

    albums: Mapped[list['Album']] = relationship('Album', back_populates='artist')


class Album(NameMixin, db.Model):
    __tablename__ = 'album'

    tracks_metadata: Mapped[list['TrackMetadata']] = relationship('TrackMetadata', back_populates='album')

    artist_id: Mapped[int | None] = mapped_column(ForeignKey('artist.id'))
    artist: Mapped['Artist | None'] = relationship('Artist', back_populates='albums')


class Tag(NameMixin, db.Model):
    __tablename__ = 'tag'
    group: Mapped[str | None] = mapped_column(String, index=True)

    tracks_metadata: Mapped[list['TrackMetadata']] = relationship(
        'TrackMetadata', secondary=track_metadata_tag_table, back_populates='tags'
    )

    @staticmethod
    def get_by_name_and_group(tag_name, tag_group):
        stmt = select(Tag).where(Tag.name == tag_name, Tag.group == tag_group)
        return db.session.execute(stmt).scalar_one_or_none()
