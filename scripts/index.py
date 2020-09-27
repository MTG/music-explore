import argparse
from pathlib import Path

import numpy as np
from tqdm import tqdm
from annoy import AnnoyIndex
import pandas as pd


def build_index(input_dir, embeddings_file, csv_file, n_dimensions, n_trees, dry=False, n_tracks=None):
    input_dir = Path(input_dir)

    embedding_files = sorted(input_dir.rglob('*.npy'))
    if len(embedding_files) == 0:
        raise RuntimeError(f'The directory is empty: {input_dir}')

    if n_tracks is not None:
        embedding_files = embedding_files[:n_tracks]

    metadata = []
    embeddings_index = AnnoyIndex(n_dimensions, 'euclidean')
    print('Processing embeddings...')
    for embedding_file in tqdm(embedding_files):
        embeddings = np.load(str(embedding_file))[:, :n_dimensions]
        last_index = len(metadata)
        for i, embedding in enumerate(embeddings):
            embeddings_index.add_item(last_index + i, embedding)
            metadata.append([embedding_file.stem, i])

    print('Building index...')
    embeddings_index.build(n_trees)

    if not dry:
        print('Saving index...')
        embeddings_index.save(embeddings_file)
        metadata_index = pd.DataFrame(metadata, columns=['track', 'segment'])
        metadata_index.to_csv(csv_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir')
    parser.add_argument('embeddings_file', help='generated annoy index file name')
    parser.add_argument('csv_file', help='csv_file that maps the annoy indexes to track_id and segment position')
    parser.add_argument('n_dimensions', type=int)
    parser.add_argument('n_trees', type=int)
    parser.add_argument('--dry', action='store_true')
    parser.add_argument('-n', '--n_tracks', default=None, type=int)
    args = parser.parse_args()
    build_index(args.input_dir, args.embeddings_file, args.csv_file, args.n_dimensions, args.n_trees, args.dry,
                args.n_tracks)
