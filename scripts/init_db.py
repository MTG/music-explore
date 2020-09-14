import argparse
from pathlib import Path

import pandas as pd

from app.database import create_tables, db_session
from app.models import Segment


def init_db(input_csv):
    create_tables()
    data = pd.read_csv(input_csv)
    print('Inserting into db...')
    db_session.bulk_insert_mappings(Segment, data.to_dict(orient='records'))
    print('Committing...')
    db_session.commit()
    print('Done!')
    db_session.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_csv')
    args = parser.parse_args()
    init_db(args.input_csv)
