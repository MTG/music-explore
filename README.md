# Music Exploration

## Requirements
Python 3.7

## Config

Copy the config file example to `instance` folder
```shell script
mkdir instance
cp config.py.dist instance/config.py
```

Edit the config:
* Point the `AUDIO_DIR` to the root of audio directories
* Point the `EMBEDDINGS_DIR` and `TAGGRAMS_DIR` to the empty directories where embeddings and taggrams will be extracted

If you want to serve audio from local server create a soft link `static/audio` pointing to audio folder and change  
`SERVE_AUDIO_LOCALLY` to `True`. Otherwise register an app in [Jamendo Dev portal](https://devportal.jamendo.com/) and 
set `JAMENDO_CLIENT_ID` variable.

## Environment

```shell script
python3.7 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Requirements file doesn't cover requirements for audio processing and offline plotting, see the following 
sections.

## Audio processing

Currently MusiCNN (v0.1.0) on PyPi is not updated with the important fix in embedding extraction, so it needs to be 
cloned and installed locally. The audio processing script has some heavy dependencies such as `tensorflow`, so they are 
not included in `requirements.txt`. It is recommended to use separate virtual environment for it.

After the fix will be deployed, it will be as easy as:
```shell script
pip install musicnn
python process.py
```

## Plotting offline

You can make some offline plots with `seaborn`. The requirements are not included in `requirements.txt`, so they need to
be installed separately. `scikit-learn` is in `requirements.txt`, it is included here if you want to use separate
virtual environment (recommended)

```shell script
pip install seaborn==0.10.0 scikit-learn==0.22.1
python -m visualize.sns
```

## Running

```shell script
python app.py
```

### Audio


##