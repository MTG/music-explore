import logging
from pathlib import Path

import click
import numpy as np
from flask import current_app
from flask.cli import with_appcontext
from tqdm import tqdm

from app.database import Track
from app.models import get_models

SAMPLE_RATE = 16000


def extract(input_dir, output_dir, algorithm, model_file, layer, accumulate=False, dry=False, force=False):
    import essentia.standard as ess  # to avoid essentia as regular dependency

    try:
        algorithm = getattr(ess, algorithm)
    except AttributeError:
        logging.error(f'No algorithm {algorithm} in essentia.standard')
        exit(1)

    input_dir = Path(input_dir)
    output_dir = Path(output_dir)

    for track in tqdm(Track.get_all()):
        audio_file = input_dir / track.path
        embeddings_file = output_dir / track.get_embeddings_filename()
        if force or not embeddings_file.exists():
            audio = ess.MonoLoader(filename=str(audio_file), sampleRate=SAMPLE_RATE)()
            embeddings = algorithm(graphFilename=str(model_file), patchHopSize=0, output=layer,
                                   accumulate=accumulate)(audio)
            if not dry:
                embeddings_file.parent.mkdir(parents=True, exist_ok=True)
                np.save(embeddings_file, embeddings)

    logging.info('Done!')


def extract_all(models_dir, accumulate=False, dry=False, force=False):
    app = current_app
    audio_dir = app.config['AUDIO_DIR']
    data_root_dir = Path(app.config['DATA_DIR'])
    models_dir = Path(models_dir)

    models = get_models()
    for model in models.get_combinations():
        logging.info(f'Extracting {model}')
        extract(
            audio_dir,
            data_root_dir / str(model),
            model.architecture_data['essentia-algorithm'],
            models_dir / f'{model.dataset}-{model.architecture}.pb',
            model.layer_data['name'],
            accumulate, dry, force
        )


# Entry points

@click.command('extract')
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.argument('algorithm')
@click.argument('model-file', type=click.Path(exists=True))
@click.option('-l', '--layer', default='model/Sigmoid', help='name of the layer to extract embeddings')
@click.option('-c', '--accumulate', is_flag=True, help='try to use single Tensorflow session for the whole file')
@click.option('-d', '--dry', is_flag=True, help='simulate the run, no writing')
@click.option('-f', '--force', is_flag=True, help='force overwriting of embedding files')
@with_appcontext
def extract_command(input_dir, output_dir, algorithm, model_file, layer, accumulate, dry, force):
    """Extract embeddings from the .mp3 audio files in INPUT_DIR and save them as .npy files in the OUTPUT_DIR keeping
    similar directory hierarchy. ALGORITHM is a class name from essentia (e.g. TensorflowPredictMusiCNN), MODEL-FILE is
    a path to a .pb file that can be used by that class"""
    extract(input_dir, output_dir, algorithm, model_file, layer, accumulate, dry, force)


@click.command('extract-all')
@click.argument('models_dir', type=click.Path(exists=True))
@click.option('-c', '--accumulate', is_flag=True, help='try to use single Tensorflow session for the whole file')
@click.option('-d', '--dry', is_flag=True, help='simulate the run')
@click.option('-f', '--force', is_flag=True, help='force overwriting of embedding files')
@with_appcontext
def extract_all_command(models_dir, accumulate, dry, force):
    """Compute all embeddings according to config file. Expects MODELS_DIR to have all dataset-model files inside named
    accordingly (e.g. mtt-musicnn.pb)"""
    extract_all(models_dir, accumulate, dry, force)
