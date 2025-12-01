#!/usr/bin/env bash
set -e

echo "IMPORTANT: make sure that you:"
echo "- have copied config-example.py to instance/config.py"
echo "- set the variables ROOT_DIR and AUDIO_DIR as absolute paths"
echo "- created the soft symlink app/static/audio pointing to your audio"

echo 'Setting up Python environment...'
uv sync --group processing

echo 'Downloading models...'
mkdir -p essentia-tf-models
cd essentia-tf-models
wget https://essentia.upf.edu/models/autotagging/msd/msd-musicnn-1.pb -O msd-musicnn.pb
wget https://essentia.upf.edu/models/autotagging/msd/msd-vgg-1.pb -O msd-vgg.pb
wget https://essentia.upf.edu/models/autotagging/mtt/mtt-musicnn-1.pb -O mtt-musicnn.pb
wget https://essentia.upf.edu/models/autotagging/mtt/mtt-vgg-1.pb -O mtt-vgg.pb
wget https://essentia.upf.edu/models/feature-extractors/vggish/audioset-vggish-3.pb -O audioset-vggish.pb
cd ..

echo 'Processing the music collection'
uv run flask init-db
uv run flask index-all-audio
uv run --group processing flask extract-all essentia-tf-models
uv run flask reduce-all
uv run flask index-all-embeddings
uv run flask aggregate-all
uv run --group processing flask load-id3-metadata

echo "Done! You can run the app now with 'uv run flask run'"
