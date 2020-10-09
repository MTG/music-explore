from pathlib import Path
from typing import Union, Generator, Tuple, List

import numpy as np
from tqdm import tqdm


def list_files(path: Union[str, Path], wildcard: str) -> List[Path]:
    """Checks if the directory is empty and returns sorted list of file paths that match wildcard"""
    path = Path(path)
    files = sorted(path.rglob(wildcard))
    if len(files) == 0:
        raise RuntimeError(f'No {wildcard} files found in {path}')
    return files


def get_embeddings(embedding_files: List[Path], n_dimensions: int = None) -> \
        Generator[np.ndarray, None, None]:
    """Iterates through all embeddings and slices the dimensions"""
    for embedding_file in tqdm(embedding_files):
        yield np.load(str(embedding_file))[:, :n_dimensions]


# check if this one is necessary
# def load_embeddings(path, n_tracks=None, n_dimensions=None):
#
#
#     embedding_files = list_files(path, '*.npy')
#
#     if n_tracks is not None:
#         embedding_files = embedding_files[:n_tracks]
#
#     if dimensions is None:
#         embeddings = [np.load(str(embedding_file)) for embedding_file in embedding_files]
#     else:
#         embeddings = [np.load(str(embedding_file))[:, dimensions] for embedding_file in embedding_files]
#
#     names = [embedding_file.stem for embedding_file in embedding_files]
#     return embeddings, names  # list of 2d matrices, list of names
