from pathlib import Path
import random

import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go

from config import EMBEDDINGS_DIR, TAGGRAMS_DIR

TSNE_MAX_DIMS = 50
EDGE_IGNORE = 0
MATPLOTLIB_FIGSIZE = [12, 10]
PYPLOT_MARKER_SCALE = 10


def load_embeddings(path: Path, n_tracks=None):
    embedding_files = sorted(path.glob('**/*.npy'))
    n_tracks = n_tracks or len(embedding_files)
    # TODO: replace with map?
    embeddings = [np.load(embedding_file) for embedding_file in embedding_files[:n_tracks]]
    names = [embedding_file.stem for embedding_file in embedding_files[:n_tracks]]
    return embeddings, names  # list of 2d matrices


def reduce(embeddings, method='pca', dimensions=2):
    embeddings_stacked = np.vstack(embeddings)
    lengths = list(map(len, embeddings))

    if method == 'tsne':
        intermediate_pca = PCA(n_components=TSNE_MAX_DIMS)
        embeddings_intermediate = intermediate_pca.fit_transform(embeddings_stacked)

        tsne = TSNE(n_components=dimensions, random_state=0)
        embeddings_reduced = tsne.fit_transform(embeddings_intermediate)

    elif method == 'pca':
        pca = PCA(n_components=dimensions)
        embeddings_reduced = pca.fit_transform(embeddings_stacked)

    else:
        raise ValueError("Method should be either 'tsne' or 'pca'")

    return np.split(embeddings_reduced, np.cumsum(lengths)[:-1])


def get_trajectories(embeddings_2d):
    lengths = list(map(len, embeddings_2d))
    embeddings_stacked = np.vstack(embeddings_2d)
    positions = [0] + np.cumsum(lengths)

    trajectories = []

    for start, end in zip(positions[:-1], positions[1:]):
        trajectories.append([embeddings_stacked[start + EDGE_IGNORE:end - EDGE_IGNORE, 0],
                             embeddings_stacked[start + EDGE_IGNORE:end - EDGE_IGNORE, 1]])
    return trajectories


def plot_trajectories_sns(embeddings_2d):
    trajectories = get_trajectories(embeddings_2d)
    plt.figure(figsize=MATPLOTLIB_FIGSIZE)
    for x, y in trajectories:
        sns.lineplot(x, y, sort=False)
    plt.show()


def get_trajectories_plotly(embeddings_2d):
    trajectories = get_trajectories(embeddings_2d)
    fig = go.Figure()
    for x, y in trajectories:
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line_shape='spline'))
    return fig


def get_averages(embeddings_2d):
    avg = np.array([item.mean(axis=0) for item in embeddings_2d])
    std = np.array([item.std(axis=0).mean() for item in embeddings_2d])
    return avg, std


def plot_averages_sns(embeddings_2d):
    avg, std = get_averages(embeddings_2d)
    plt.figure(figsize=MATPLOTLIB_FIGSIZE)
    sns.scatterplot(avg[:, 0], avg[:, 1], size=std)
    plt.show()


def get_averages_plotly(embeddings_2d, names):
    avg, std = get_averages(embeddings_2d)
    fig = go.Figure(data=go.Scatter(
        x=avg[:, 0],
        y=avg[:, 1],
        mode='markers',
        marker=dict(size=std * PYPLOT_MARKER_SCALE),
        hovertext=names,
        hoverinfo='text'
    ))
    return fig


def get_plotly_fig(source, plot_type, n_tracks, method):
    if source == 'embeddings':
        path = Path(EMBEDDINGS_DIR)
    elif source == 'taggrams':
        path = Path(TAGGRAMS_DIR)
    else:
        raise ValueError("data should be either 'embeddings' or 'taggrams'")

    embeddings, names = load_embeddings(path, n_tracks=n_tracks)
    embeddings_reduced = reduce(embeddings, method=method)

    if plot_type == 'averages':
        fig = get_averages_plotly(embeddings_reduced, names)
    elif plot_type == 'trajectories':
        fig = get_trajectories_plotly(embeddings_reduced)
    else:
        raise ValueError("plot_type should be either 'averages' or 'trajectories'")

    return fig


def main():
    path = Path(TAGGRAMS_DIR)
    embeddings, _ = load_embeddings(path, n_tracks=20)
    embeddings_reduced = reduce(embeddings, method='tsne')

    plot_trajectories_sns(embeddings_reduced)
    plot_averages_sns(embeddings_reduced)


if __name__ == '__main__':
    main()
