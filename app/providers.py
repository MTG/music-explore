from pathlib import Path

from flask import Blueprint, current_app, url_for

from .database import Segment, Track


bp = Blueprint('providers', __name__, url_prefix='/audio')


def get_jamendo_url(jamendo_id):
    client_id = current_app.config["JAMENDO_CLIENT_ID"]
    return f'https://mp3l.jamendo.com/?trackid={jamendo_id}&format=mp31&from=app-{client_id}'


def get_track_url(track):
    provider = current_app.config['AUDIO_PROVIDER']
    if provider == 'local':
        return url_for('static', filename=Path('audio') / track.path)

    if provider == 'jamendo':
        return get_jamendo_url(track.jamendo_id)

    # TODO: make in ConfigException that it caught everywhere in Flask
    raise Exception('Wrong audio provider {provider} in the configuration')


@bp.route('/track/<int:track_id>')
def get_track_url_api(track_id):
    track = Track.get_by_id(track_id)
    return {
        'url': get_track_url(track),
        'text': track.track_metadata.to_text()
    }


@bp.route('/segment/<int:segment_id>')
def get_segment_url(segment_id):
    segment = Segment.get_by_id(segment_id)
    track_url = get_track_url(segment.track)
    return {
        'url': f'{track_url}{segment.get_url_suffix()}',
        'text': segment.track.track_metadata.to_text()
    }
