# Logging
LOGGING_FORMAT = '%(asctime)s %(levelname)s %(message)s'
LOGGING_LEVEL = 'DEBUG'

# Annoy
ANNOY_DISTANCE = 'euclidean'
ANNOY_TREES = 16

# Models
MODELS_FILE = 'models.yaml'

# Directories
ROOT_DIR = '/path/to/app-root'
AUDIO_DIR = f'{ROOT_DIR}/audio'  # directory with audio files, can have nested directories
DATA_DIR = f'{ROOT_DIR}/data'  # directory for extracted embeddings
INDEX_DIR = f'{ROOT_DIR}/annoy'  # directory for indexed embeddings

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
