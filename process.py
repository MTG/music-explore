from pathlib import Path
import logging

from musicnn.extractor import extractor
import numpy as np

from config import EMBEDDINGS_FILE, IDS_FILE, AUDIO_DIR

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

 
def process():
    path = Path(AUDIO_DIR)
    audio_files = sorted(path.glob('**/*.mp3'))[:1]

    ids = []
    embeddings = []

    total = len(audio_files)
    for i, audio_file in enumerate(audio_files):
        taggram, tags, features = extractor(audio_file, model='MTT_musicnn', extract_features=True)
        features_penultimate = features['penultimate']
        embeddings.append(features_penultimate[0])
        ids.append(audio_file.stem)
        logger.info(f'{i+1}/{total}')

    embeddings = np.array(embeddings, dtype=np.float32)
    ids = np.array(ids)

    np.save(EMBEDDINGS_FILE, embeddings)
    np.save(IDS_FILE, ids)


if __name__ == '__main__':
    process()
