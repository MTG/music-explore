# Music Exploration

## Development

## Requirements

Python 3.7+

### Config

Copy the config file example to `instance` folder
```shell script
mkdir instance
cp config-example.py instance/config.py
```

Edit the config:
* Point the `EMBEDDINGS_DIR` to the directory with `penultimate` and `taggrams` embeddings

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

### Extracting embeddings *(to be updated)*

Currently MusiCNN (v0.1.0) on PyPi is not updated with the important fix in embedding extraction, so it needs to be 
cloned and installed locally. The audio processing script has some heavy dependencies such as `tensorflow`, so they are 
not included in `requirements.txt`. It is recommended to use separate virtual environment for it.

After the fix will be deployed, it will be as easy as:
```shell script
pip install musicnn
python process.py
```

### Applying PCA

```shell script
python scripts/reduce_offline.py /path/to/embeddings/penultimate /path/to/embeddings/penultimate_pca pca
python scripts/reduce_offline.py /path/to/embeddings/taggrams /path/to/embeddings/taggrams_pca pca
```

## Plotting offline *(to be updated)*

You can make some offline plots with `seaborn`. The requirements are not included in `requirements.txt`, so they need to
be installed separately. `scikit-learn` is in `requirements.txt`, it is included here if you want to use separate
virtual environment (recommended)

```shell script
pip install seaborn==0.10.0 scikit-learn==0.22.1
python -m visualize.sns
```
