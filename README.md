# Music Exploration

## Requirements
Python 3.7

## Development

```shell script
python3.7 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

```shell script
mkdir instance
cp config.py instance
```

## Data

Download the embeddings for the data and point the config path to correct location.
* Embeddings
* Taggrams

For serving audio from local server create a soft link `static/audio` pointing to audio folder and change the config 
`SERVE_AUDIO_LOCALLY` to `True`
