from sklearn.decomposition import PCA
import numpy as np


def analyze_component_variance(projection: PCA, cutoff=10):
    print('Components ratios:')
    variances = projection.explained_variance_ratio_[:cutoff]
    diffs = np.insert(-np.diff(variances), 0, 0)
    print(f'PC  indiv  cumul  diff')
    for i, (variance, cumsum, diff) in enumerate(zip(variances, np.cumsum(variances), diffs)):
        print(f'{i+1:2}: {variance:.3f}, {cumsum:.3f}, {diff:.3f}')


def analyze_projection_matrix(projection: PCA, size, cutoff=10, labels=None):
    for i in range(cutoff):
        vector = np.zeros(size)
        vector[i] = 1
        print(projection.inverse_transform(vector))


def analyze_data_dimensions(data, cutoff=10, labels=None):
    print('Dimensions with highest standard deviations:')
    variances = data.var(axis=0)
    indices = np.argsort(variances)[::-1]
    indices = indices[:cutoff]
    print('Tag variance')
    for i, deviation in zip(indices, variances[indices]):
        print(f'{i:2}: {deviation:.3f}')


def analyze_pca():
    pass
