import json

import numpy as np
import plotly
import plotly.graph_objects as go
from flask import Blueprint, current_app, request

from .database.base import Track
from .database.metadata import TrackMetadata
from .models import Model, get_models
from .processing.reduce import reduce_tsne, reduce_umap

bp = Blueprint('plot', __name__)

PLOTLY_MARGINS = {'l': 40, 'r': 0, 't': 30, 'b': 40}
PLOTLY_MARKER_SCALE = 10


def get_averages(embeddings):
    avg = np.array([item.mean(axis=0) for item in embeddings])
    std = np.array([item.std(axis=0).mean() for item in embeddings])
    std = std / std.std()
    return avg, std


def plot_averages(embeddings, tracks):
    avg, std = get_averages(embeddings)
    fig = go.Figure(data=go.Scatter(
        x=avg[:, 0],
        y=avg[:, 1],
        mode='markers',
        marker={'size': std * PLOTLY_MARKER_SCALE},
        hovertext=[track.track_metadata.to_text() for track in tracks],
        hoverinfo='text',
        ids=[track.full_id for track in tracks],
        # marker_color=[track.track_metadata.artist_id for track in tracks]
    ))
    return fig


def get_trajectories(embeddings):
    lengths = list(map(len, embeddings))
    embeddings_stacked = np.vstack(embeddings)
    positions = np.insert(np.cumsum(lengths), 0, 0)

    trajectories = []

    for start, end in zip(positions[:-1], positions[1:]):
        trajectories.append([embeddings_stacked[start:end, 0],
                             embeddings_stacked[start:end, 1]])
    return trajectories, lengths


def plot_segments(embeddings, tracks, segment_length, show_trajectories=False):
    trajectories, lengths = get_trajectories(embeddings)  # TODO: check if needed
    fig = go.Figure()

    mode = 'lines+markers' if show_trajectories else 'markers'
    args = {} if show_trajectories else {'marker_color': plotly.colors.qualitative.Plotly[0]}

    for (x, y), length, track in zip(trajectories, lengths, tracks):
        segments = track.get_segments(segment_length)
        track_text = track.track_metadata.to_text()
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode=mode,
            ids=[segment.full_id for segment in segments],
            hovertext=[f'{track_text} ({segment.to_text()})' for segment in segments],
            hoverinfo='text',
            name=track_text,
            showlegend=False,
            line_shape='spline',
            **args
        ))
    return fig


def get_plotly_fig(plot_type, embeddings, tracks, model):
    """
    Parses plot_type and calls corresponding plot function.
    :raises ValueError: invalid plot_type
    """
    if plot_type == 'averages':
        fig = plot_averages(embeddings, tracks)
    elif plot_type in ['trajectories', 'segments']:
        fig = plot_segments(embeddings, tracks, model.length, show_trajectories=(plot_type == 'trajectories'))
    else:
        raise ValueError(f"Invalid plot_type: {plot_type}, should be 'averages', 'trajectories' or 'segments'")

    fig.update_layout(
        margin=PLOTLY_MARGINS
    )
    return fig


@bp.route('/plot/<string:plot_type>/<string:dataset>/<string:architecture>/<string:layer>/<int:n_tracks>/'
          '<projection>/<int:x>/<int:y>')
def plot(plot_type, dataset, architecture, layer, n_tracks, projection, x, y):
    try:
        dynamic_projection = projection in ['tsne', 'umap']

        # TODO: maybe validate dataset-model-layer?
        if projection == 'original':
            model_projection = None
        elif dynamic_projection:  # t-sne and umap uses pca as input
            model_projection = 'pca'
        else:  # 'pca', 'std-pca'
            model_projection = projection
        model = Model(get_models().data, dataset, architecture, layer, model_projection)

        tracks = Track.get_all(limit=n_tracks, random=False)

        dimensions = slice(current_app.config['PCA_DIMS']) if dynamic_projection else [x, y]

        embeddings = model.get_embeddings(tracks, dimensions=dimensions)

        # TODO: time the projection, alert user if it is too slow?
        if projection == 'tsne':
            embeddings = reduce_tsne(embeddings)
        elif projection == 'umap':
            embeddings = reduce_umap(embeddings)

        figure = get_plotly_fig(plot_type, embeddings, tracks, model)

        # add labels on axis if those are tags
        if projection == 'original' and layer == 'taggrams':
            tags = model.dataset_data['tags']
            figure.update_layout(
                xaxis_title=tags[x],
                yaxis_title=tags[y]
            )
        # TODO: add proper labels for other modes

    except ValueError as e:
        return {'error': str(e)}, 400
    except FileNotFoundError as e:
        return {'error': str(e)}, 404

    return json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)


def plot_segments_advanced(embeddings, tracks, segment_length, sparse_factor, highlight_ids, use_webgl):
    fig = go.Figure()
    scale = plotly.colors.qualitative.Plotly

    # groups = {}

    for track_embeddings, track in zip(embeddings, tracks):
        segments = track.get_segments(segment_length, sparse_factor)
        track_text = track.track_metadata.to_text()

        # group_id = track.track_metadata.artist_id
        # if group_id not in groups:
        #     groups[group_id] = len(groups)

        scatter = go.Scattergl if use_webgl else go.Scatter
        fig.add_trace(scatter(
            x=track_embeddings[:, 0],
            y=track_embeddings[:, 1],
            mode='markers',
            ids=[segment.full_id for segment in segments],
            hovertext=[f'{track_text} ({segment.to_text()})' for segment in segments],
            hoverinfo='text',
            name=track_text,
            showlegend=False,
            # marker={'color': scale[groups[group_id]]}
            # marker={'color': scale[0]}
            marker={'color': scale[1] if track.id in highlight_ids else scale[0]}
        ))

    return fig


def _append(result: dict, name: str, value: str):
    if name not in result:
        result[name] = []
    result[name].append(value)


def get_highlight_groups(tracks_meta):
    results = {
        'artist': {},
        'album': {},
        'track': {},
        'tag': {}
    }
    for track_meta in tracks_meta:
        _append(results['artist'], track_meta.artist.name, track_meta.id)
        _append(results['album'], track_meta.album.name, track_meta.id)
        _append(results['track'], track_meta.name, track_meta.id)
        for tag in track_meta.tags:
            _append(results['tag'], tag.name, track_meta.id)
    return results


@bp.route('/plot-advanced', methods=['POST'])
def plot_advanced():
    # tracks
    data_query = request.json['data']
    tag_ids = [int(tag) for tag in data_query['tags']]
    artist_ids = [int(artist) for artist in data_query['artists']]
    tracks_meta = TrackMetadata.get_by_tags_and_artists(tag_ids, artist_ids)
    tracks = [track_meta.track for track_meta in tracks_meta]

    sparse_factor = int(data_query['sparse'])
    use_webgl = data_query['webgl']

    # highlight
    highlight_ids = request.json['highlight']
    # logging.info(highlight_ids)

    # models
    result_plots = {}
    for plot_side, model_query in request.json['models'].items():
        projection = model_query['projection']
        if projection == 'original':
            projection = None

        model = Model(get_models().data, model_query['dataset'], model_query['architecture'],
                      model_query['layer'], projection)

        embeddings = get_embeddings_and_project(model, tracks, sparse_factor)

        figure = plot_segments_advanced(embeddings, tracks, model.length, sparse_factor, highlight_ids, use_webgl)
        figure.update_layout(margin=PLOTLY_MARGINS)
        # result_plots[plot_side] = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)
        result_plots[plot_side] = figure.to_dict()

    highlight_groups = get_highlight_groups(tracks_meta)

    return json.dumps({
        'plots': result_plots,
        'highlight': highlight_groups
    }, cls=plotly.utils.PlotlyJSONEncoder)


def get_embeddings_and_project(model, tracks, sparse_factor):
    if 'pca' in model.projection:
        return model.get_embeddings(tracks, sparse_factor, [0, 1])

    embeddings = model.with_projection('pca').get_embeddings(
        tracks, sparse_factor, slice(current_app.config['PCA_DIMS']))

    if model.projection == 'tsne':
        return reduce_tsne(embeddings)

    if model.projection == 'umap':
        return reduce_umap(embeddings)
