from flask import Blueprint, render_template

from .database.metadata import Artist, Tag
from .models import get_models
from .similarity import get_segments

bp = Blueprint('views', __name__)


@bp.route('/')
@bp.route('/playground')
def playground():
    models = get_models()
    return render_template('playground.html',
                           datasets=models.get_triplets('datasets'),
                           architectures=models.get_triplets('architectures'),
                           tags=models.get_dict('datasets', 'tags'))


@bp.route('/compare')
def compare():
    return render_template('compare.html',
                           data=get_models().data,
                           artists=sorted(Artist.get_all()),
                           tags=sorted(Tag.get_all()))


@bp.route('/similarity')
def explore():
    segments = get_segments()
    return render_template('similarity.html', segments=segments)
