# Music Exploration

## Setup

### Requirements

Python 3.7+

### Config

Copy the config file example to `instance` folder
```shell
mkdir instance
cp config-example.py instance/config.py
```

Edit the config:
* Point the `ROOT_DIR` to the empty directory where all the data will be stored
* Point the `AUDIO_DIR` to the directory with all the audio files

If you are using own collection of audio, to serve audio from local server create a soft link `app/static/audio`
pointing to your audio folder and make sure that `AUDIO_PROVIDER` is set to `local`.
```shell
ln -s /path/to/your/audio app/static/audio
```

If you are using [mtg-jamendo-dataset](https://github.com/MTG/mtg-jamendo-dataset), you can serve audio directly
from Jamendo servers by registering an app in [Jamendo Dev portal](https://devportal.jamendo.com/) and setting
`JAMENDO_CLIENT_ID` variable. In this case make sure that `AUDIO_PROVIDER` is set to `jamendo`.

### Environment

```shell
python3.x -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

If you get an error while installing `annoy`, make sure that you have `python3.x-dev` installed

You can use python 3.8+ with no problems for running the app, but you will need separate environment for audio
processing, as, there are no `essentia-tensorflow` wheels for Python 3.8 yet.
However, it is a good idea to have separate environments for processing and running anyway, as there are some packages
that are only used for processing.

Additional processing libraries:
* `tensorflow-essentia`: extracting embeddings (has no wheels for Python 3.8 yet, 380MB):
```
pip install essentia-tensorflow
```
* `tinytag`: install it if you use personal music collection, it parses ID3 tags
```
pip install essentia-tensorflow tinytag
```

### Download essentia-tensorflow models

```shell
mkdir essentia-tf-models
cd essentia-tf-models
wget https://essentia.upf.edu/models/autotagging/msd/msd-musicnn-1.pb -O msd-musicnn.pb
wget https://essentia.upf.edu/models/autotagging/msd/msd-vgg-1.pb -O msd-vgg.pb
wget https://essentia.upf.edu/models/autotagging/mtt/mtt-musicnn-1.pb -O mtt-musicnn.pb
wget https://essentia.upf.edu/models/autotagging/mtt/mtt-vgg-1.pb -O mtt-vgg.pb
wget https://essentia.upf.edu/models/feature-extractors/vggish/audioset-vggish-3.pb -O audioset-vggish.pb
```

If you don't want to use all models, feel free to comment out entries in `app/models.yaml`

Embedding layers for the models:
| Model   | Layer                                        | Size          |
|---------|----------------------------------------------|---------------|
| MusiCNN | model/batch_normalization_10/batchnorm/add_1 | 200           |
| VGG     | model/flatten/Reshape                        | 2 x 128 = 256 |
| VGGish  | model/vggish/fc2/BiasAdd                     | 128           |

If you don't have a lot of tracks, feel free to add `tsne` to `offline_projections` in `app/models.yaml`. By default
t-SNE is applied dynamically only on the number of tracks that you are visualizing at a time.

### Process audio

```shell
flask init-db  # creates tables in db
flask index-all-audio  # creates list of audio tracks in db
flask extract-all essentia-tf-models  # extracts embeddings
flask reduce-all  # computes the projections
flask index-all-embeddings  # indexes everything in database
```

#### Adding local metadata
```shell
flask load-id3-metadata
```

#### Adding Jamendo metadata
Clone or download metadata from [mtg-jamendo-dataset]((https://github.com/MTG/mtg-jamendo-dataset))
```shell
flask load-jamendo-data path/to/mtg-jamendo-dataset/data/raw_30s_cleantags.tsv
```

Query Jamendo API for track, artist, album names
```
# TODO
```

### Running the app

```shell
FLASK_ENV=development flask run
```

## Deploying with Docker (to be updated)

- Set `SERVE_AUDIO_LOCALLY` in `config-docker.py` appropriately depending if you want to use Jamendo API or not
- Build and run docker image with your data mounted at `/data`, it uses port 80 by default
- If `SERVE_AUDIO_LOCALLY=True`, make sure to mount your audio dir at `/app/static/audio` otherwise make sure that you
set `JAMENDO_CLIENT_ID` environment variable

Example:
```shell script
docker build -t music-explore .
docker run -p 8080:80 -v /path/to/data:/data -v /path/to/audio:/app/static/audio music-explore  # run with local audio
docker run -p 8080:80 -v /path/to/data:/data --env JAMENDO_CLIENT_ID=XXXXXXXX music-explore  # run with Jamendo API
```

## Development

```
pip install pre-commit
pre-commit install
```


## License

The code is licensed under [GNU Affero General Public License v3.0](/LICENSE).

## Citation

When using or referencing this work, please cite the following publication:
```
@inproceedings{tovstogan2020web,
  title = {Web Interface for Exploration of Latent and Tag Spaces in Music Auto-Tagging},
  author = {Philip Tovstogan and Xavier Serra and Dmitry Bogdanov},
  booktitle = {Machine Learning for Media Discovery Workshop, ML4MD, International Conference on Machine Learning, ICML 2020},
  year = {2020}
}
```

## Acknowledgments

This project has received funding from the European Union's Horizon 2020 research and innovation programme under the
Marie Skłodowska-Curie grant agreement No. 765068.

<img src="https://upload.wikimedia.org/wikipedia/commons/b/b7/Flag_of_Europe.svg" height="64" alt="Flag of Europe">
