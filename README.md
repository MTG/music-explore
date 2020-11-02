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
* Point the `ROOT_DIR` to the directory where you want to store all data, ideally with `audio` directory inside having
 audio files

If you want to serve audio from local server create a soft link `app/static/audio` pointing to audio folder and make 
sure that `AUDIO_PROVIDER` is set to `local`. 
```shell
ln -s /path/to/your/root/audio app/static/audio
```

If you are using [mtg-jamendo-dataset](https://github.com/MTG/mtg-jamendo-dataset), you can serve audio directly 
from Jamendo servers by registering an app in [Jamendo Dev portal](https://devportal.jamendo.com/) and setting 
`JAMENDO_CLIENT_ID` variable. In this case make sure that `AUDIO_PROVIDER` is set to `jamendo`.

### Environment

```shell
python3.8 -m venv venv
source venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt
pip install essentia-tensorflow  # this requirement is only needed for processing the audio, you can uninstall later
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

### Process audio

```shell
flask init-db
flask index-all-audio
flask extract-all essentia-tf-models
flask reduce-all
flask index-all-embeddings
```

Embedding layers for the models:
| Model   | Layer                                        | Size          |
|---------|----------------------------------------------|---------------|
| MusiCNN | model/batch_normalization_10/batchnorm/add_1 | 200           |
| VGG     | model/flatten/Reshape                        | 2 x 128 = 256 |
| VGGish  | model/vggish/fc2/BiasAdd                     | 128           |

### Running

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

## Jamendo metadata integration
```shell
flask load-jamendo-data /path/to/raw_30s_cleantags.tsv
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
