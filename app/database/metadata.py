from sqlalchemy import Column, ForeignKey, Integer, String, Table, or_
from sqlalchemy.orm import relationship

from .base import CommonMixin, db


class NameMixin(CommonMixin):
    name = Column(String, index=True)

    @classmethod
    def get_by_name(cls, name):
        return db.session.query(cls).filter_by(name=name).first()

    def __lt__(self, other):
        return (self.name is None, self.name) < (other.name is None, other.name)


track_metadata_tag_table = Table('track_metadata_tag', db.Model.metadata,
                                 Column('tag_id', Integer, ForeignKey('tag.id')),
                                 Column('track_id', Integer, ForeignKey('track_metadata.id'))
                                 )


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
