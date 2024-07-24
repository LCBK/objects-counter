import os

INSTANCE_PATH = '/instance'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = '/uploads'
DB_NAME = 'object_counter.sqlite'
MAX_DB_STRING_LENGTH = 255
SAM_CHECKPOINT = os.environ.get('SAM_CHECKPOINT', os.path.join(INSTANCE_PATH + 'sam_vit_h_4b8939.pth'))
