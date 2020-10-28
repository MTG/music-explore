from flask import Blueprint, render_template

from .models import get_models

bp = Blueprint('views', __name__)


@bp.route('/')
@bp.route('/playground')
def playground():
    models = get_models()
    return render_template('playground.html',
                           datasets=models.get_triplets('datasets'),
                           architectures=models.get_triplets('architectures'),
                           tags=models.get_dict('datasets', 'tags'))


@bp.route('/explore')
def explore():
    track_ids = ['1022300:27:30', '1080900:0:3', '1080900:30:33']
    return render_template('explore.html', audio_urls=[])  # [get_audio_url(track_id)['url'] for track_id in track_ids]
