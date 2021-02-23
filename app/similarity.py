from flask import Blueprint, request

from .database import Segment

bp = Blueprint('similarity', __name__)


def get_segments():
    length = 3000
    ref_segment_id = 1000
    segment_choices_id = [2000, 3000, 4000]
    segment_choices = [Segment.get_by_id(length, segment_id) for segment_id in segment_choices_id]
    return {
        'reference': Segment.get_by_id(length, ref_segment_id),
        'choices': segment_choices
    }


@bp.route('/similarity-result', methods=['POST'])
def process_result():
    reference = request.json['reference']
    choices = request.json['choices']
    selected = request.json['selected']
    print(reference, choices, selected)
    return {}, 200
