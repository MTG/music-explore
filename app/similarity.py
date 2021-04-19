import csv
import random
from pathlib import Path
from time import time
from typing import Optional

from flask import Blueprint, current_app, request

from .database.base import Segment, Segmentation
from .models import Model, get_models

bp = Blueprint('similarity', __name__)


def get_segments(strategy: str = 'semirandom', model: Optional[Model] = None):
    length = 3000

    if strategy == 'static':
        ref_segment_id = 1000
        segment_choices_id = [2000, 3000, 4000]
        segment_choices = [Segment.get_by_id(length, segment_id) for segment_id in segment_choices_id]

        return {
            'reference': Segment.get_by_id(length, ref_segment_id),
            'choices': segment_choices
        }

    if strategy == 'semirandom':
        total = Segmentation.get_total_segments(length)
        ref_segment_id = random.randint(0, total)
        ref_segment = Segment.get_by_id(length, ref_segment_id)
        ref_artist = ref_segment.track.track_metadata.artist

        if model is None:
            models = []
            for model in get_models().get_combinations():
                if model.length == length:
                    models.append(model)

            model = random.choice(models)
        index = model.get_annoy_index()

        closest_segment = None
        closest_n = 2
        while closest_segment is None:
            print(f'looking from {closest_n//2} .. {closest_n}')
            for segment_id in index.get_nns_by_item(ref_segment_id, closest_n + 1)[closest_n // 2:]:
                segment = Segment.get_by_id(length, segment_id)
                if segment.track.track_metadata.artist != ref_artist:
                    closest_segment = segment
            closest_n *= 2

        random_segments = [Segment.get_by_id(length, random.randint(0, total)) for _ in range(2)]
        random_segments.append(closest_segment)
        random.shuffle(random_segments)

        distances = [index.get_distance(ref_segment_id, segment.id) for segment in random_segments]

        return {
            'reference': ref_segment,
            'choices': random_segments,
            'closest': closest_segment,
            'distances': distances,
            'model': model
        }


def get_id(full_id: str):
    return full_id.split('/')[2] if full_id else full_id  # segment/3000/1100 -> 1100, '' -> ''


@bp.route('/similarity-result', methods=['POST'])
def process_result():
    reference = request.json['reference']
    choices = request.json['choices']
    selected = request.json['selected']

    experiments_dir = Path(current_app.config['EXPERIMENTS_DIR'])
    length = reference.split('/')[1]

    results = [int(time()), request.json['model'], get_id(reference), get_id(selected)]
    results += [get_id(choice) for choice in choices if choice != selected]

    results_file = experiments_dir / f'{length}.csv'
    results_file.parent.mkdir(exist_ok=True)

    with results_file.open('a') as fp:
        writer = csv.writer(fp)
        writer.writerow(results)

    return {}, 200
