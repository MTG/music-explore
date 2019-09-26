from pathlib import Path

from flask import current_app
from musicnn.extractor import extractor


def process():
    path = Path(current_app.config['AUDIO_DIR'])
    audio_files = sorted(path.glob('**/*.mp3'))[:1]

    for audio_file in audio_files:
        taggram, tags, features = extractor(audio_file, model='MTT_musicnn', extract_features=True)
        current_app.logger.info(features['penultimate'])
