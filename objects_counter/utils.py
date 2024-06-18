from objects_counter.db.models import db, Image, User, Result  # pylint: disable=unused-import


def config_db(app, db_name):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.init_app(app)
    with app.app_context():
        db.create_all()
