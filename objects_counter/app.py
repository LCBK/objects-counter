import os
import sys

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate


from objects_counter.utils import config_logging, config_db

# pylint: disable=wrong-import-position
config_logging()  # noqa: E402
SERVICE_MODE = sys.argv[1] != 'run'  # noqa: E402
if not SERVICE_MODE:
    from objects_counter.api.common import blueprint, api
from objects_counter.consts import UPLOAD_FOLDER, DB_NAME
from objects_counter.db.models import db, bcrypt


app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev'
)

CORS(app)

app.config.from_pyfile('config.py', silent=True)

app.config['UPLOAD_FOLDER'] = os.path.join(app.instance_path, UPLOAD_FOLDER)
app.config['THUMBNAIL_FOLDER'] = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails')

try:
    os.makedirs(app.instance_path)
except FileExistsError:
    pass

try:
    os.makedirs(app.config["UPLOAD_FOLDER"])
except FileExistsError:
    pass

try:
    os.makedirs(app.config["THUMBNAIL_FOLDER"])
except FileExistsError:
    pass

if not SERVICE_MODE:
    api.init_app(app, add_specs=False)
    app.register_blueprint(blueprint)

config_db(app, DB_NAME)
bcrypt.init_app(app)

migrate = Migrate(app, db)
