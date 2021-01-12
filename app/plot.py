import json

import numpy as np
import plotly
import plotly.graph_objects as go
from flask import Blueprint

from .database import Track
from .models import Model, get_models
from .processing.reduce import reduce_tsne

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
        tsne_dynamic = 'tsne' not in models_data['offline_projections'] and projection == 'tsne'

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

        embeddings = model.get_embeddings_from_annoy(tracks, dimensions)
        # embeddings = model.get_embeddings_from_file(tracks, dimensions)

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
