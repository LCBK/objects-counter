import os

from flask import Flask
from flask_cors import CORS

from objects_counter.api import blueprint, api
from objects_counter.consts import UPLOAD_FOLDER


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'object_counter.sqlite'),
    )

    CORS(app)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

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

    return app
