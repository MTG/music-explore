from pathlib import Path

import click
import numpy as np
import pandas as pd
from flask.cli import with_appcontext

from app.database.base import Segment, Segmentation


def get_url_suffix(segment_length, segment_id):
    print(segment_length, segment_id)
    segment = Segment.get_by_id(segment_length, segment_id)
    return segment.get_url_suffix()


def generate_pairs(output_dir: Path, n_queries: int, n_candidates: int, segment_length: int = 3000):
    total = Segmentation.get_total_segments(segment_length)
    ids = np.random.randint(total, size=(n_queries, n_candidates + 1))
    print(ids)

    suffixes = []
    for ids_row in ids:
        row = []
        for id_value in ids_row:
            row.append(get_url_suffix(segment_length, id_value))
        suffixes.append(row)

    output_dir.mkdir(exist_ok=True, parents=True)
    np.save(str(output_dir / 'ids.npy'))
    pd.DataFrame(suffixes).to_csv(str(output_dir / 'suffixes.csv'), header=False, index=False)


@click.command('rater_generate_pairs')
@click.argument('output_dir', type=Path)
@click.option('--n-queries', type=int, default=10)
@click.option('--n-candidates', type=int, default=5)
@click.option('--length', type=int, default=3000)
@with_appcontext
def generate_pairs_command(output_dir, n_queries, n_candidates, length):
    generate_pairs(output_dir, n_queries, n_candidates, length)
