import os

# Flask
ENV = 'production'
DEBUG = False

# Data, expects directories in format {dataset}-{model}-{layer}[-pca]
DATA_DIR = '/data/'

# Audio
SERVE_AUDIO_LOCALLY = False  # if True make sure to mount /app/static/audio
JAMENDO_CLIENT_ID = os.environ.get("JAMENDO_CLIENT_ID")  # else set JAMENDO_CLIENT_ID environment variable
