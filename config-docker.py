import os

# Flask
ENV = 'production'
DEBUG = False

# Logging
LOGGING_FORMAT = '%(asctime)s %(levelname)s %(message)s'
LOGGING_LEVEL = 'INFO'

# Annoy
ANNOY_DISTANCE = 'angular'
ANNOY_TREES = 16

# Models
MODELS_FILE = 'models.yaml'

# Data, expects directories in format {dataset}-{model}-{layer}[-pca]
ROOT_DIR = '/data/'
INDEX_DIR = f'{ROOT_DIR}/annoy'  # directory for indexed embeddings
AGGRDATA_DIR = f'{ROOT_DIR}/aggrdata'  # directory for aggregated embeddings

# Constants
SEGMENT_PRECISION = 1  # number of digits to show after period for seconds for url hash

# Database
SQLALCHEMY_DATABASE_URI = f'sqlite:///{ROOT_DIR}/db.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False  # to suppress warnings about deprecated functionality in sqlalchemy

# Number of items that are committed at a time: higher number speeds up processing but if something goes wrong,
# more data will be lost
DB_COMMIT_BATCH_SIZE = 1000

# Audio
AUDIO_PROVIDER = 'jamendo'  # can be 'jamendo' for mtg-jamendo-dataset, or 'local' for in-house collection

# Jamendo - ignore if not using Jamendo
JAMENDO_CLIENT_ID = os.environ.get("JAMENDO_CLIENT_ID")
JAMENDO_BATCH_SIZE = 100  # number of tracks to include in one API call to Jamendo when populating the metadata

# Experiments results
EXPERIMENTS_DIR = f'{ROOT_DIR}/results'  # where to store similarity results

# Plots
PCA_DIMS = 10  # number of PCA dimensions that are used for tsne and umap
