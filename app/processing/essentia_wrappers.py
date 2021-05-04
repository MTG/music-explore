from __future__ import annotations

from pathlib import Path
from typing import Optional

import essentia.standard as ess
import numpy as np
from essentia import Pool

SAMPLE_RATE = 16000


def get_predictors(models_dir: Path, architectures: dict) -> dict:
    predictors = {}
    for architecture, metadata in architectures.items():
        output_layers = [item['name'] for item in metadata['layers'].values()]
        for dataset in metadata['datasets']:
            predictors[f'{dataset}-{architecture}'] = ess.TensorflowPredict(
                graphFilename=str(models_dir / f'{dataset}-{architecture}.pb'),
                inputs=['model/Placeholder'], outputs=output_layers,
            )

    return predictors


def get_melspecs(audio_file: Path, algorithms: dict) -> Optional[dict[str, np.ndarray]]:
    # loading file
    audio = ess.MonoLoader(filename=str(audio_file), sampleRate=SAMPLE_RATE)()

    # precompute melspecs
    melspecs_all = {}
    for algorithm_name in algorithms:
        parameters = algorithms[algorithm_name]

        melspec_extractor = getattr(ess, parameters['melspec-algorithm'])()
        melspecs = []
        for frame in ess.FrameGenerator(audio, frameSize=parameters['frame-size'], hopSize=parameters['hop-size']):
            melspecs.append(melspec_extractor(frame))

        melspecs = np.array(melspecs)

        # reshape melspecs into tensor batches and discard the remainder
        discard = melspecs.shape[0] % parameters['patch-size']
        if discard != 0:
            melspecs = melspecs[:-discard, :]
        melspecs = np.reshape(melspecs, [-1, parameters['patch-size'], parameters['number-bands']])
        batch = np.expand_dims(melspecs, 2)

        melspecs_all[algorithm_name] = batch

    return melspecs_all


def get_embeddings(melspecs: dict[str, np.ndarray], architectures: dict, predictors: dict) -> Optional[dict]:
    data = {}
    for architecture, metadata in architectures.items():
        input_pool = Pool()
        input_pool.set('model/Placeholder', melspecs[metadata['essentia-algorithm']])

        for dataset in metadata['datasets']:
            output_pool = predictors[f'{dataset}-{architecture}'](input_pool)

            for layer, layer_data in metadata['layers'].items():
                embeddings = output_pool[layer_data['name']].squeeze()

                if len(embeddings) == 0:
                    return None

                data[f'{dataset}-{architecture}-{layer}'] = embeddings

    return data
