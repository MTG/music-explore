from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns

from visualize.commons import load_embeddings, reduce, get_trajectories, get_averages
from instance.config import PENULTIMATE_DIR, TAGGRAMS_DIR

MATPLOTLIB_FIGSIZE = [12, 10]


def plot_trajectories_sns(embeddings_2d):
    trajectories, _ = get_trajectories(embeddings_2d)
    plt.figure(figsize=MATPLOTLIB_FIGSIZE)
    for x, y in trajectories:
        sns.lineplot(x, y, sort=False)
    plt.show()


def plot_averages_sns(embeddings_2d):
    avg, std = get_averages(embeddings_2d)
    plt.figure(figsize=MATPLOTLIB_FIGSIZE)
    sns.scatterplot(avg[:, 0], avg[:, 1], size=std)
    plt.show()


def main():
    path = Path(TAGGRAMS_DIR)
    embeddings, _ = load_embeddings(path, n_tracks=20)
    embeddings_reduced = reduce(embeddings, projection_type='tsne')

    plot_trajectories_sns(embeddings_reduced)
    plot_averages_sns(embeddings_reduced)


if __name__ == '__main__':
    main()
