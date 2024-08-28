import logging

from objects_counter.consts import LOG_LEVEL
from objects_counter.db.models import db


def config_db(app, db_name):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.init_app(app)


def config_logging():
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('objects_counter.log')
        ]
    )
