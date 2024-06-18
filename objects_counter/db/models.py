from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# pylint: disable=too-few-public-methods

class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filepath = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)


class Result(db.Model):
    __tablename__ = 'result'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey(Image.id), nullable=False)
    objects_count = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())
    user = db.relationship('User', backref='results')
    image = db.relationship('Image', backref='results')
