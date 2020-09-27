from sqlalchemy import Column, Integer
import pandas as pd
import click
from flask.cli import with_appcontext

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Segment(db.Model):
    __tablename__ = 'segments'
    length = 3.0
    id = Column(Integer, primary_key=True, index=True)
    track = Column(Integer, index=True)
    position = Column(Integer)

    def __repr__(self):
        return f'{self.track}:{self.position * self.length}:{(self.position + 1) * self.length}'

    def get_vector(self, type, model):
        pass


@click.command('init-db')
@with_appcontext
def init_db():
    db.create_all()
    click.echo('Created all tables')


@click.command('load-segments')
@click.argument('csv_file')
@with_appcontext
def load_segments(csv_file):
    data = pd.read_csv(csv_file)
    click.echo('Loading data into database...')
    db.session.bulk_insert_mappings(Segment, data.to_dict(orient='records'))
    click.echo('Committing...')
    db.session.commit()
    click.echo('Finished')


def init_app(app):
    db.init_app(app)
    app.cli.add_command(init_db)
    app.cli.add_command(load_segments)
