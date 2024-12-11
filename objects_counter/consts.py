import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'uploads'
DB_NAME = 'objects_counter'
DB_ADDRESS = os.environ.get('DB_ADDRESS', 'localhost:5432')
DB_USERNAME = 'lcbk'
DB_PASSWORD = os.environ.get('DB_PASSWORD')
MIN_USERNAME_LENGTH = 4
MAX_DB_STRING_LENGTH = 255
SAM_CHECKPOINT = os.environ.get('SAM_CHECKPOINT')
SAM_MODEL_TYPE = os.environ.get('SAM_MODEL_TYPE', 'vit_h')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
