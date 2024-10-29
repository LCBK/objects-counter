from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

# pylint: disable=too-few-public-methods


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filepath = db.Column(db.String(255), nullable=False)
    thumbnail = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())
    background_points = db.Column(db.JSON, nullable=True)
    result = db.relationship('Result', backref='image', uselist=False)
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=True)
    dataset = db.relationship('Dataset', backref='images')


class ImageElement(db.Model):
    __tablename__ = 'image_element'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_id = db.Column(db.Integer, db.ForeignKey(Image.id), nullable=False)
    top_left = db.Column(db.JSON, nullable=False)
    bottom_right = db.Column(db.JSON, nullable=False)
    classification = db.Column(db.String(255), nullable=True)
    certainty = db.Column(db.Float, nullable=True)
    image = db.relationship('Image', backref='elements')

    def as_dict(self):
        return {
            'id': self.id,
            'top_left': self.top_left,
            'bottom_right': self.bottom_right,
            'certainty': self.certainty,
        }


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)


class Result(db.Model):
    __tablename__ = 'result'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey(Image.id), nullable=False)
    data = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())
    user = db.relationship('User', backref='results')

    def as_dict(self):
        return {
            'id': self.id,
            'user': self.user.username,
            'image_id': self.image_id,
            'data': self.data,
            'timestamp': self.timestamp
        }


class Dataset(db.Model):
    __tablename__ = 'dataset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship('User', backref='datasets')

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user': self.user.username,
            'timestamp': self.timestamp,
            'images': [image.id for image in self.images]
        }
