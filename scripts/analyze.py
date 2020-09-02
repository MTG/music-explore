from sklearn.decomposition import PCA
import numpy as np


def analyze_component_variance(projection: PCA, cutoff=10):
    print('Components ratios:')
    variances = projection.explained_variance_ratio_[:cutoff]
    for i, (variance, variance_cumulative) in enumerate(zip(variances, np.cumsum(variances))):
        print(f'PC-{i+1:2}: {variance:.3f}, {variance_cumulative:.3f}')


def analyze_projection_matrix(projection: PCA, size, labels=None):
    vector = np.zeros(size)
    vector[0] = 1
    print(projection.inverse_transform(vector))


def analyze_pca():
    pass
