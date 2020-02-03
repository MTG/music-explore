from pathlib import Path
import logging

from musicnn.extractor import extractor
import numpy as np

from instance.config import AUDIO_DIR, EMBEDDINGS_DIR, TAGGRAMS_DIR

logger = logging.getLogger(__file__)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def process():
    path = Path(AUDIO_DIR)
    audio_files = sorted(path.glob('**/*.mp3'))[:]
    total = len(audio_files)
    logger.info(f'Starting, files to be processed: {total}')

    for i, audio_file in enumerate(audio_files):
        relative_path = audio_file.relative_to(AUDIO_DIR).with_suffix('.npy')
        embeddings_file = Path(EMBEDDINGS_DIR) / relative_path
        taggram_file = Path(TAGGRAMS_DIR) / relative_path
        status = 'skipped'
        if not embeddings_file.exists() or not taggram_file.exists():
            embeddings_file.parent.mkdir(parents=True, exist_ok=True)
            taggram_file.parent.mkdir(parents=True, exist_ok=True)
            taggram, tags, features = extractor(audio_file, model='MTT_musicnn', extract_features=True)
            np.save(embeddings_file, features['penultimate'])
            np.save(taggram_file, taggram)
            status = 'processed'
        logger.info(f'Audio {audio_file.stem:>8} ({i+1:>5}/{total:>5}) - {status}')


if __name__ == '__main__':
    process()
