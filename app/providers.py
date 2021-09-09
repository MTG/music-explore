from __future__ import annotations

from pathlib import Path, PurePosixPath, PureWindowsPath

from flask import Blueprint, Response, current_app, request, url_for

from .database.base import Segment, Track

bp = Blueprint('providers', __name__, url_prefix='/audio')


def get_jamendo_url(jamendo_id):
    client_id = current_app.config["JAMENDO_CLIENT_ID"]
    return f'https://mp3l.jamendo.com/?trackid={jamendo_id}&format=mp31&from=app-{client_id}'


def get_track_url(track, for_playlist=False):
    provider = current_app.config['AUDIO_PROVIDER']
    if provider == 'local':
        if for_playlist and current_app.config.get('PLAYLIST_FOR_OFFLINE'):
            path_cls = PureWindowsPath if current_app.config.get('PLAYLIST_USE_WINDOWS_PATH') else PurePosixPath
            root_dir = current_app.config.get('PLAYLIST_AUDIO_DIR') or current_app.config['AUDIO_DIR']
            return str(path_cls(root_dir) / track.path)

        else:
            return url_for('static', filename=Path('audio') / track.path, _external=True)

    if provider == 'jamendo':
        return get_jamendo_url(track.jamendo_id)

    # TODO: make in ConfigException that it caught everywhere in Flask
    raise Exception('Wrong audio provider {provider} in the configuration')


@bp.route('/track/<int:track_id>')
def get_track_url_api(track_id):
    track = Track.get_by_id(track_id)
    return {
        'url': get_track_url(track),
        'text': track.track_metadata.to_text(),
        'tags': track.track_metadata.tags_to_text()
    }


@bp.route('/segment/<int:segment_length>/<int:segment_id>')
def get_segment_url(segment_length, segment_id):
    segment = Segment.get_by_id(segment_length, segment_id)
    track_url = get_track_url(segment.track)
    return {
        'url': f'{track_url}{segment.get_url_suffix()}',
        'text': segment.track.track_metadata.to_text(),
        'tags': segment.track.track_metadata.tags_to_text()
    }


# Playlists
def generate_playlist_body(tracks: list[Track]):
    urls = [get_track_url(track, for_playlist=True) for track in tracks]
    return '\n'.join(urls)


@bp.route('/playlist', methods=['POST'])
def to_playlist():
    segments = request.json['segments']
    tracks = []
    for segment_str in segments:
        _, segment_length, segment_id = segment_str.split('/')
        segment = Segment.get_by_id(int(segment_length), int(segment_id))
        track = segment.track
        if track not in tracks:
            tracks.append(track)

    playlist_body = generate_playlist_body(sorted(tracks, key=lambda _track: _track.id))
    return Response(playlist_body, mimetype='audio/mpegurl')
