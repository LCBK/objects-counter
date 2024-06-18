import os

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from objects_counter.api import blueprint, api
from objects_counter.consts import UPLOAD_FOLDER, DB_NAME
from objects_counter.db.models import db, bcrypt
from objects_counter.utils import config_db


app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'object_counter.sqlite'),
)

CORS(app)

app.config.from_pyfile('config.py', silent=True)

app.config['UPLOAD_FOLDER'] = app.instance_path + UPLOAD_FOLDER

try:
    os.makedirs(app.instance_path)
except FileExistsError:
    pass

try:
    os.makedirs(app.config["UPLOAD_FOLDER"])
except FileExistsError:
    pass

api.init_app(app, add_specs=False)
app.register_blueprint(blueprint)

config_db(app, DB_NAME)
bcrypt.init_app(app)

migrate = Migrate(app, db)
