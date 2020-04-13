# Flask
ENV = 'development'
DEBUG = True

# Data
DATA_DIR = '/path/to/data/jamendo-dataset/'
EMBEDDINGS_DIR = DATA_DIR  # expects directories `penultimate` and `taggrams`
USE_PRECOMPUTED_PCA = True  # if this is set to True, app will look for `penultimate_pca` and `taggrams_pca` dirs

# API
SERVE_AUDIO_LOCALLY = False
JAMENDO_CLIENT_ID = ''

