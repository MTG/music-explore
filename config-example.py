# Logging
LOGGING_FORMAT = '%(asctime)s %(levelname)s %(message)s'
LOGGING_LEVEL = 'DEBUG'

# Annoy
ANNOY_DISTANCE = 'euclidean'
ANNOY_TREES = 16

# Models
MODELS_FILE = 'models.yaml'

# Directories
ROOT_DIR = '/path/to/root'
AUDIO_DIR = f'{ROOT_DIR}/audio'  # directory with audio files, can have nested directories
DATA_DIR = f'{ROOT_DIR}/data'  # directory for extracted embeddings
INDEX_DIR = f'{ROOT_DIR}/annoy'  # directory for indexed embeddings

# Database
SQLALCHEMY_DATABASE_URI = f'sqlite:///{ROOT_DIR}/db.sqlite'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Audio
AUDIO_PROVIDER = 'jamendo'  # can be 'jamendo' for mtg-jamendo-dataset, or 'local' for in-house collection

# Jamendo - ignore if not using Jamendo
JAMENDO_CLIENT_ID = ''
JAMENDO_METADATA_FILE = ''
