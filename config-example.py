# Logging
LOGGING_FORMAT = '%(asctime)s %(levelname)s %(message)s'
LOGGING_LEVEL = 'INFO'

# Annoy
ANNOY_DISTANCE = 'angular'
ANNOY_TREES = 16

# Models
MODELS_FILE = 'models-anon.yaml'

# Directories
ROOT_DIR = '/path/to/root'
AUDIO_DIR = f'{ROOT_DIR}/audio'  # directory with audio files, can have nested directories
DATA_DIR = f'{ROOT_DIR}/data'  # directory for extracted embeddings
INDEX_DIR = f'{ROOT_DIR}/annoy'  # directory for indexed embeddings
AGGRDATA_DIR = f'{ROOT_DIR}/aggrdata'  # directory for aggregated embeddings

# PLAYLIST_FOR_OFFLINE = True  # set it to true if you want to generate playlists for offline listening
# PLAYLIST_USE_WINDOWS_PATH = True  # set it to True if you are using WSL - affects the paths generated for playlists
# PLAYLIST_AUDIO_DIR = 'D:\\path\\to\\audio'  # if the offline audio path is different (WSL, or maybe media center)

# Constants
SEGMENT_PRECISION = 1  # number of digits to show after period for seconds for url hash

# Database
SQLALCHEMY_DATABASE_URI = f'sqlite:///{ROOT_DIR}/db.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False  # to suppress warnings about deprecated functionality in sqlalchemy

# Number of items that are committed at a time: higher number speeds up processing but if something goes wrong,
# more data will be lost
DB_COMMIT_BATCH_SIZE = 1000

# Audio
AUDIO_PROVIDER = 'local'  # can be 'jamendo' for mtg-jamendo-dataset, or 'local' for in-house collection

# Jamendo - ignore if not using Jamendo
JAMENDO_CLIENT_ID = ''
JAMENDO_BATCH_SIZE = 100  # number of tracks to include in one API call to Jamendo when populating the metadata

# Experiments results
EXPERIMENTS_DIR = f'{ROOT_DIR}/results'  # where to store similarity results

# Plots
PCA_DIMS = 10  # number of PCA dimensions that are used for tsne and umap

# Flask-Caching related configs
CACHE_TYPE = 'SimpleCache'
CACHE_DEFAULT_TIMEOUT = 600
