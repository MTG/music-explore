from .extract import extract_all_command, extract_command
from .index_audio import index_all_audio_command, index_audio_command
from .index_embeddings import index_all_embeddings_command, index_embeddings_command
from .metadata.id3 import load_id3_metadata_command
from .metadata.jamendo import load_jamendo_metadata_command
from .reduce import reduce_all_command, reduce_command


def init_app(app):
    app.cli.add_command(extract_command)
    app.cli.add_command(extract_all_command)
    app.cli.add_command(reduce_command)
    app.cli.add_command(reduce_all_command)
    app.cli.add_command(index_embeddings_command)
    app.cli.add_command(index_all_embeddings_command)
    app.cli.add_command(index_audio_command)
    app.cli.add_command(index_all_audio_command)
    app.cli.add_command(load_jamendo_metadata_command)
    app.cli.add_command(load_id3_metadata_command)
