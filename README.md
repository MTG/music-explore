# Music Exploration

## Development

### Requirements

Python 3.7+

### Config

Copy the config file example to `instance` folder
```shell script
mkdir instance
cp config-example.py instance/config.py
```

Edit the config:
* Point the `DATA_DIR` to the directory with `embeddings` and `taggrams` directory

If you want to serve audio from local server create a soft link `app/static/audio` pointing to audio folder and change  
`SERVE_AUDIO_LOCALLY` to `True`. Otherwise register an app in [Jamendo Dev portal](https://devportal.jamendo.com/) and 
set `JAMENDO_CLIENT_ID` variable.

### Environment

```shell script
python3.7 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Requirements file doesn't cover requirements for audio processing and offline plotting, see the following sections.

### Running

```shell script
python app/main.py
```

## Deploying with Docker

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

## Creating data

### Extracting embeddings

To learn more about essentia-tensorflow, see this 
[blog post](https://mtg.github.io/essentia-labs/news/2020/01/16/tensorflow-models-released/), here are just a list of 
steps

```shell script
python -m venv venv_process  # Create separate virtual environment
source venv_process/bin/activate
pip install --upgrade pip wheel
pip install -f https://essentia.upf.edu/python-wheels/ essentia-tensorflow  # install essentia-tensorflow
pip install tqdm  # install other dependencies
wget https://essentia.upf.edu/models/autotagging/mtt/mtt-musicnn.pb  # download the model
python scripts/process_essentia.py /path/to/audio /path/to/embeddings/mtt-musicnn-taggrams musicnn mtt-musicnn.pb  # extract taggrams
python scripts/process_essentia.py /path/to/audio /path/to/embeddings/mtt-musicnn-embeddings musicnn mtt-musicnn.pb --layer=model/batch_normalization_10/batchnorm/add_1  # extract taggrams
```

Embedding layers for the models:
| Model   | Layer                                        | Size          |
|---------|----------------------------------------------|---------------|
| MusiCNN | model/batch_normalization_10/batchnorm/add_1 | 200           |
| VGG     | model/flatten/Reshape                        | 2 x 128 = 256 |
| VGGish  | model/vggish/fc2/BiasAdd                     | 128           |

### Applying PCA

```shell script
python scripts/reduce_offline.py /path/to/mtt-musicnn-taggrams /path/to/mtt-musicnn-taggrams-pca pca
```

## Plotting offline *(to be updated)*

You can make some offline plots with `seaborn`. The requirements are not included in `requirements.txt`, so they need to
be installed separately. `scikit-learn` is in `requirements.txt`, it is included here if you want to use separate
virtual environment (recommended)

```shell script
pip install seaborn==0.10.0 scikit-learn==0.22.1
python -m visualize.sns
```

## Acknowledgments

This project has received funding from the European Union's Horizon 2020 research and innovation programme under the 
Marie Skłodowska-Curie grant agreement No. 765068.

<img src="https://upload.wikimedia.org/wikipedia/commons/b/b7/Flag_of_Europe.svg" height="64" alt="Flag of Europe">
