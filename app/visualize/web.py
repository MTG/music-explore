import numpy as np
import plotly.graph_objects as go
import plotly.colors as colors

from visualize.commons import get_trajectories, get_averages

PLOTLY_MARGINS = dict(l=40, r=0, t=30, b=40)
PLOTLY_MARKER_SCALE = 10


def get_segments_plotly(embeddings_2d, names, segment_length, show_trajectories=False):
    trajectories, lengths = get_trajectories(embeddings_2d)
    fig = go.Figure()
    mode = 'lines+markers' if show_trajectories else 'markers'
    args = {} if show_trajectories else {'marker_color': colors.qualitative.Plotly[0], 'showlegend': False}
    for (x, y), name, length in zip(trajectories, names, lengths):
        ids = list(map(lambda s: f'{name}:{s:.2f}:{s + segment_length:.2f}', np.arange(0, length) * segment_length))
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode=mode,
            ids=ids,
            hovertext=ids,
            hoverinfo='text',
            name=name,
            line_shape='spline',
            **args
        ))
    return fig


def get_averages_plotly(embeddings_2d, names):
    avg, std = get_averages(embeddings_2d)
    fig = go.Figure(data=go.Scatter(
        x=avg[:, 0],
        y=avg[:, 1],
        mode='markers',
        marker=dict(size=std * PLOTLY_MARKER_SCALE),
        hovertext=names,
        hoverinfo='text',
        ids=names
    ))
    return fig


def get_plotly_fig(embeddings, names, plot_type, segment_length):
    if plot_type == 'averages':
        fig = get_averages_plotly(embeddings, names)
    elif plot_type == 'trajectories':
        fig = get_segments_plotly(embeddings, names, segment_length, show_trajectories=True)
    elif plot_type == 'segments':
        fig = get_segments_plotly(embeddings, names, segment_length, show_trajectories=False)
    else:
        raise ValueError(f"Invalid plot_type: {plot_type}, should be 'averages', 'trajectories' or 'segments'")

    fig.update_layout(
        margin=PLOTLY_MARGINS
    )
    return fig
