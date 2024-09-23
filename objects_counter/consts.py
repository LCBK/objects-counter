import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'uploads'
DB_NAME = 'object_counter.sqlite'
MAX_DB_STRING_LENGTH = 255
SAM_CHECKPOINT = os.environ.get('SAM_CHECKPOINT')
SAM_MODEL_TYPE = os.environ.get('SAM_MODEL_TYPE', 'vit_h')
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
