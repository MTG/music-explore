from pathlib import Path

import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns

from config import EMBEDDINGS_DIR, TAGGRAMS_DIR


def get_embeddings():
    path = Path(EMBEDDINGS_DIR)
    embedding_files = sorted(path.glob('**/*.npy'))[:1]

    for i, embedding_file in enumerate(embedding_files):
        embeddings = np.load(embedding_file)
        pca = PCA(n_components=2)
        embeddings_pca = pca.fit_transform(embeddings)

        plt.figure(figsize=(16, 10))
        sns.lineplot(embeddings_pca[:, 0], embeddings_pca[:, 1], sort=False)
        plt.show()


if __name__ == '__main__':
    get_embeddings()
