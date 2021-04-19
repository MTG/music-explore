import json

import numpy as np
import plotly
import plotly.graph_objects as go
from flask import Blueprint, request

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
        marker_color=[track.track_metadata.artist_id for track in tracks]
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
            hovertext=[segment.to_text() for segment in segments],
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
        models_data = get_models().data
        tsne_dynamic = 'tsne' not in models_data['offline-projections'] and projection == 'tsne'

        # TODO: maybe validate dataset-model-layer?
        if projection == 'original':
            model_projection = None
        elif tsne_dynamic:  # t-sne uses pca as input
            model_projection = 'pca'
        else:  # 'pca', 'std-pca'
            model_projection = projection
        model = Model(get_models().data, dataset, architecture, layer, model_projection)

        tracks = Track.get_all(limit=n_tracks, random=False)

        dimensions = None if tsne_dynamic else [x, y]  # TODO: load limited amount of dimensions for tsne

        # embeddings = model.get_embeddings_from_annoy(tracks, dimensions)
        # embeddings = model.get_embeddings_from_file(tracks, dimensions)
        embeddings = model.get_embeddings_from_aggrdata(tracks, dimensions)

        if tsne_dynamic:  # TODO: try moving tsne to browser
            embeddings = reduce_tsne(embeddings)

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


def plot_segments_advanced(embeddings, tracks, segment_length):
    fig = go.Figure()
    scale = plotly.colors.qualitative.Plotly

    groups = {}

    for track_embeddings, track in zip(embeddings, tracks):
        segments = track.get_segments(segment_length)
        track_text = track.track_metadata.to_text()

        group_id = track.track_metadata.artist_id
        if group_id not in groups:
            groups[group_id] = len(groups)

        fig.add_trace(go.Scatter(
            x=track_embeddings[:, 0],
            y=track_embeddings[:, 1],
            mode='markers',
            ids=[segment.full_id for segment in segments],
            hovertext=[segment.to_text() for segment in segments],
            hoverinfo='text',
            name=track_text,
            showlegend=False,
            marker={'color': scale[groups[group_id]]}
            # marker={'color': scale[0]}
        ))
    return fig


@bp.route('/plot-advanced', methods=['POST'])
def plot_advanced():
    request_model = request.json['model']
    request_filters = request.json['filters']

    projection = request_model['projection']
    if projection == 'original':
        projection = None

    model = Model(get_models().data, request_model['dataset'], request_model['architecture'],
                  request_model['layer'], projection)

    tag_ids = [int(tag) for tag in request_filters['tags']]
    artist_ids = [int(artist) for artist in request_filters['artists']]
    tracks_meta = TrackMetadata.get_by_tags_and_artists(tag_ids, artist_ids)

    tracks = [track_meta.track for track_meta in tracks_meta]
    embeddings = get_embeddings_and_project(model, tracks)

    figure = plot_segments_advanced(embeddings, tracks, model.length)
    figure.update_layout(margin=PLOTLY_MARGINS)

    return json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)


def get_embeddings_and_project(model, tracks):
    if 'pca' in model.projection:
        return model.get_embeddings_from_aggrdata(tracks, [0, 1])

    embeddings = model.with_projection('pca').get_embeddings_from_aggrdata(tracks, slice(20))

    if model.projection == 'tsne':
        return reduce_tsne(embeddings)

    if model.projection == 'umap':
        return reduce_umap(embeddings)
