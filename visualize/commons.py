from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

TSNE_MAX_DIMS = 50
EDGE_IGNORE = 0


def load_embeddings(path: Path, n_tracks=None):
    embedding_files = sorted(path.glob('**/*.npy'))
    if len(embedding_files) == 0:
        raise ValueError(f'No data available, maybe path is wrong: {path}')
    n_tracks = n_tracks or len(embedding_files)
    # TODO: replace with map?
    embeddings = [np.load(str(embedding_file)) for embedding_file in embedding_files[:n_tracks]]
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

    elif isinstance(method, tuple):
        if not len(method) == 2:
            raise ValueError("Method tuple should have length of 2")
        embeddings_reduced = embeddings_stacked[:, method]

    else:
        raise ValueError("Method should be 'tsne', 'pca' or a tuple of dimensions (e.g. (10, 11))")

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
    print(f'Standard deviations = {std}')
    return avg, std

