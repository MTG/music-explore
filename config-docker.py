import os

# Flask
ENV = 'production'
DEBUG = False

# Data
DATA_DIR = '/data/'
EMBEDDINGS_DIR = DATA_DIR
USE_PRECOMPUTED_PCA = True

# Audio
SERVE_AUDIO_LOCALLY = False  # if True make sure to mount /app/static/audio
JAMENDO_CLIENT_ID = os.environ.get("JAMENDO_CLIENT_ID")  # else set JAMENDO_CLIENT_ID environment variable
