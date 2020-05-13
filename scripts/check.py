import argparse
from pathlib import Path

import numpy as np
from tqdm import tqdm


def check(input_dir, expected_dimensions, num_files):
    input_dir = Path(input_dir)
    embeddings_files = sorted(input_dir.rglob('*.npy'))
    if len(embeddings_files) == 0:
        raise ValueError(f'No data available, maybe path is wrong: {input_dir}')

    if num_files is not None:
        embeddings_files = embeddings_files[:num_files]

    files = [embeddings_file for embeddings_file in tqdm(embeddings_files)
             if np.load(embeddings_file).shape[1] != expected_dimensions]
    if len(files) > 0:
        print(f'Found {len(files)} files with wrong number of dimensions')
        response = input('Delete them? (y/n) ')
        if response == 'y':
            for embeddings_file in tqdm(files):
                embeddings_file.unlink()
    else:
        print('No files found with the wrong number of dimensions')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir')
    parser.add_argument('dimensions', type=int, help='number of expected dimensions of latent space')
    parser.add_argument('-n', '--num-files', type=int, default=None, help='number of files to check')
    args = parser.parse_args()

    check(args.input_dir, args.dimensions, args.num_files)
