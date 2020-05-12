from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

EDGE_IGNORE = 0


def load_embeddings(path: Path, n_tracks=None, dimensions=None):
    embedding_files = sorted(path.rglob('*.npy'))
    if len(embedding_files) == 0:
        raise ValueError(f'No data available, maybe path is wrong: {path}')

    if n_tracks is not None:
        embedding_files = embedding_files[:n_tracks]

    print(dimensions)
    if dimensions is None:
        embeddings = [np.load(str(embedding_file)) for embedding_file in embedding_files]
    else:
        embeddings = [np.load(str(embedding_file))[:, dimensions] for embedding_file in embedding_files]

    names = [embedding_file.stem for embedding_file in embedding_files]
    return embeddings, names  # list of 2d matrices, list of names


def reduce(embeddings, projection_type, n_dimensions_out=None, n_dimensions_in=None, verbose=False):
    if projection_type == 'tsne':
        projection = TSNE(n_components=n_dimensions_out, random_state=0, verbose=verbose)
    elif projection_type == 'pca':
        projection = PCA(n_components=n_dimensions_out, random_state=0)
    else:
        raise ValueError(f'Invalid projection_type: {projection_type}')

    embeddings_stacked = np.vstack(embeddings)
    lengths = list(map(len, embeddings))

    if n_dimensions_in is not None:
        embeddings_stacked = embeddings_stacked[:, :n_dimensions_in]

    embeddings_reduced = projection.fit_transform(embeddings_stacked)

    return np.split(embeddings_reduced, np.cumsum(lengths)[:-1])


def get_trajectories(embeddings_2d):
    lengths = list(map(len, embeddings_2d))
    embeddings_stacked = np.vstack(embeddings_2d)
    positions = np.insert(np.cumsum(lengths), 0, 0)

    trajectories = []

    for start, end in zip(positions[:-1], positions[1:]):
        trajectories.append([embeddings_stacked[start + EDGE_IGNORE:end - EDGE_IGNORE, 0],
                             embeddings_stacked[start + EDGE_IGNORE:end - EDGE_IGNORE, 1]])
    return trajectories, lengths


def get_averages(embeddings_2d):
    avg = np.array([item.mean(axis=0) for item in embeddings_2d])
    std = np.array([item.std(axis=0).mean() for item in embeddings_2d])
    std = std / std.std()
    # print(f'Standard deviations = {std}')
    return avg, std
