from sqlalchemy import Column, Integer, String, ForeignKey, exists
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import click
from flask.cli import with_appcontext


db = SQLAlchemy()


class Track(db.Model):
    __tablename__ = 'track'
    id = Column(Integer, primary_key=True)
    segments = relationship('Segment', back_populates='track')
    path = Column(String, index=True)

    def has_segments(self, session, length):
        return session.query(Segment).filter_by(track_id=self.id, length=length).first() is not None
        # TODO: make it more elegant


class Segment(db.Model):
    __tablename__ = 'segment'
    id = Column(Integer, primary_key=True)
    length = Column(Integer, primary_key=True)  # in ms

    track_id = Column(Integer, ForeignKey('track.id'))
    track = relationship('Track', back_populates='segments')
    position = Column(Integer)

    def __repr__(self):
        return f'{self.track_id}:{self.get_time()}'

    def get_time(self):
        start, stop = self.get_timestamps()
        return f'{start:.3}:{stop:.3}'

    def get_timestamps(self):
        """Returns start and end timestamps in seconds"""
        return self.position * self.length / 1000, (self.position + 1) * self.length / 1000


@click.command('init-db')
@with_appcontext
def init_db():
    db.create_all()
    click.echo('Created all tables')


def init_app(app):
    db.init_app(app)
    app.cli.add_command(init_db)
