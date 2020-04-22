from pathlib import Path
import argparse

import numpy as np
from tqdm import tqdm
from essentia.standard import MonoLoader, TensorflowPredictMusiCNN, TensorflowPredictVGGish

SAMPLE_RATE = 16000

ALGORITHMS = {
    'musicnn': TensorflowPredictMusiCNN,
    'vgg': TensorflowPredictMusiCNN,
    'vggish': TensorflowPredictVGGish
}

PENULTIMATE_LAYER = {
    'musicnn': 'model/dense/BiasAdd',
    'vgg': '?',
    'vggish': '?'
}

OUTPUT_LAYER =


def process_essentia(input_dir, output_dir, architecture, model, penultimate, accumulate, dry):
    input_dir = Path(input_dir)
    audio_files = sorted(input_dir.rglob('*.mp3'))
    if len(audio_files) == 0:
        raise RuntimeError(f'The directory is empty: {input_dir}')

    output_dir = Path(output_dir)
    if not dry:
        output_dir.mkdir(exist_ok=True)

    algorithm = ALGORITHMS[architecture]
    output_layer = PENULTIMATE_LAYER[architecture] if penultimate else OUTPUT_LAYER

    for audio_file in tqdm(audio_files):
        relative_path = audio_file.relative_to(input_dir).with_suffix('.npy')
        embeddings_file = output_dir / relative_path
        if not embeddings_file.exists():
            audio = MonoLoader(filename=str(audio_file), sampleRate=SAMPLE_RATE)()
            embeddings = algorithm(graphFilename=model, patchHopSize=0, output=output_layer,
                                   accumulate=accumulate)(audio)
            if not dry:
                embeddings_file.parent.mkdir(parents=True, exist_ok=True)
                np.save(embeddings_file, embeddings)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_dir')
    parser.add_argument('output_dir')
    parser.add_argument('architecture', choices=['musicnn', 'vgg', 'vggish'])
    parser.add_argument('model', help='path to .pb file')
    parser.add_argument('--layer', default='model/Sigmoid', help='layer of the embeddings to extract')
    parser.add_argument('--accumulate', action='store_true', help='use single Tensorflow session for the whole file')
    parser.add_argument('--dry', action='store_true', help='dry run')
    args = parser.parse_args()

    process_essentia(args.input_dir, args.output_dir, args.architecture, args.model, args.penultimate, args.accumulate,
                     args.dry)
