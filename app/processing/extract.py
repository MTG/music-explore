from pathlib import Path

import numpy as np
from tqdm import tqdm
import essentia.standard as ess
import click
from flask.cli import with_appcontext
from flask import current_app

from app.utils import list_files
from app.models import get_models

SAMPLE_RATE = 16000


def extract(input_dir, output_dir, algorithm, model_file, layer, accumulate=False, dry=False, force=False):
    try:
        algorithm = getattr(ess, algorithm)
    except AttributeError:
        raise RuntimeError(f'No algorithm {algorithm} in essentia.standard')

    audio_files = list_files(input_dir, '*.mp3')

    output_dir = Path(output_dir)
    if not dry:
        output_dir.mkdir(exist_ok=True)

    for audio_file in tqdm(audio_files):
        relative_path = audio_file.relative_to(input_dir).with_suffix('.npy')
        embeddings_file = output_dir / relative_path
        if not embeddings_file.exists() or force:
            audio = ess.MonoLoader(filename=str(audio_file), sampleRate=SAMPLE_RATE)()
            embeddings = algorithm(graphFilename=model_file, patchHopSize=0, output=layer,
                                   accumulate=accumulate)(audio)
            if not dry:
                embeddings_file.parent.mkdir(parents=True, exist_ok=True)
                np.save(embeddings_file, embeddings)


@click.command('extract')
@click.argument('input_dir', type=click.Path(exists=True))
@click.argument('output_dir', type=click.Path())
@click.option('-a', '--algorithm', help='class name from essentia (e.g. TensorflowPredictMusiCNN)')
@click.option('-m', '--model-file', type=click.Path(exists=True), help='path to protobuf file')
@click.option('-l', '--layer', default='model/Sigmoid', help='name of the layer to extract embeddings')
@click.option('-c', '--accumulate', is_flag=True, help='try to use single Tensorflow session for the whole file')
@click.option('-d', '--dry', is_flag=True, help='simulate the run, no writing')
@click.option('-f', '--force', is_flag=True, help='force overwriting of embedding files')
def extract_command(input_dir, output_dir, algorithm, model_file, layer='model/Sigmoid', accumulate=False, dry=False,
                    force=False):
    """Extract embeddings from the .mp3 audio files in INPUT_DIR and save them as .npy files in the OUTPUT_DIR keeping
    similar directory hierarchy"""
    extract(input_dir, output_dir, algorithm, model_file, layer, accumulate, dry, force)


@click.command('extract-all')
@click.argument('models_dir', type=click.Path(exists=True))
@click.option('-c', '--accumulate', is_flag=True, help='try to use single Tensorflow session for the whole file')
@click.option('-d', '--dry', is_flag=True, help='simulate the run, no writing')
@click.option('-f', '--force', is_flag=True, help='force overwriting of embedding files')
@with_appcontext
def extract_all_command(models_dir, accumulate=False, dry=False, force=False):
    """Compute all embeddings according to config file. Expects MODELS_DIR to have all dataset-model files inside named
    accordingly (e.g. mtt-musicnn.pb)"""
    app = current_app
    audio_dir = app.config['AUDIO_DIR']
    data_root_dir = Path(app.config['DATA_DIR'])
    models_dir = Path(models_dir)

    models = get_models()
    for algorithm, dataset_model, layer, layer_name in models.get_combinations():
        click.echo(f'Extracting {dataset_model}-{layer}')
        data_dir = data_root_dir / f'{dataset_model}-{layer}'
        model_file = models_dir / f'{dataset_model}.pb'
        extract(audio_dir, data_dir, algorithm, model_file, layer_name, accumulate, dry, force)
