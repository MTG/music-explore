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
                           tags=models.get_dict('datasets', 'tags'),
                           layers=models.get_triplets('layers'),
                           projections=models.get_triplets('projections')
                           )


@bp.route('/compare')
def compare():
    return render_template('compare.html',
                           data=get_models().data,
                           artists=sorted(Artist.get_all()),
                           tags=sorted(Tag.get_all()))


@bp.route('/similarity')
def explore():
    segments = get_segments()
    closest_idx = segments['choices'].index(segments['closest']) + 1
    return render_template('similarity.html', segments=segments, closest_idx=closest_idx)
