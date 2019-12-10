from pathlib import Path
import random

import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns

from config import EMBEDDINGS_DIR, TAGGRAMS_DIR


def load_embeddings(path: Path, n_tracks):
    embedding_files = sorted(path.glob('**/*.npy'))[:n_tracks]
    if n_tracks is not None:
        embedding_files = embedding_files[:n_tracks]
    else:
        n_tracks = len(embedding_files)

    embeddings_avg = []
    embeddings_std = []
    embeddings_all = []

    for i, embedding_file in enumerate(embedding_files):
        embeddings = np.load(embedding_file)
        embeddings_all.append(embeddings)
        embeddings_avg.append(embeddings.mean(axis=0))
        embeddings_std.append(embeddings.std(axis=0).mean())

    return embeddings_avg, embeddings_std, embeddings_all


def get_embeddings(method='pca', dimensions=2, n_tracks=20, average=True, fit_on_all=True):
    if method == 'tsne':
        reduction = TSNE(n_components=dimensions)
    elif method == 'pca':
        reduction = PCA(n_components=dimensions)
    else:
        raise ValueError("Method should be either 'tsne' or 'pca'")

    path = Path(TAGGRAMS_DIR)
    embeddings_avg, embeddings_std, embeddings_all = load_embeddings(path, n_tracks)

    if average:
        embedding_avg_2d = reduction.fit_transform(np.array(embeddings_avg))
        sns.scatterplot(embedding_avg_2d[:, 0], embedding_avg_2d[:, 1], size=embeddings_std)
    else:
        lengths = list(map(len, embeddings_all))
        positions = [0] + np.cumsum(lengths)
        embeddings_together = np.vstack(embeddings_all)
        embeddings_together_2d = reduction.fit_transform(embeddings_together)
        for start, end in zip(positions[:-1], positions[1:]):
            sns.lineplot(embeddings_together_2d[start+2:end-2, 0], embeddings_together_2d[start+2:end-2, 1], sort=False)

    plt.show()


if __name__ == '__main__':
    random.seed(0)
    get_embeddings()
