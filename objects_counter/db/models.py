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
    result_id = db.Column(db.Integer, db.ForeignKey('result.id'), nullable=True)
    result = db.relationship('Result', backref='images')
    dataset_id = db.Column(db.Integer, db.ForeignKey('dataset.id'), nullable=True)
    dataset = db.relationship('Dataset', backref='images')

    def as_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'background_points': self.background_points,
            'elements': [element.as_dict() for element in self.elements]
        }


class ImageElement(db.Model):
    __tablename__ = 'image_element'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    image_id = db.Column(db.Integer, db.ForeignKey(Image.id), nullable=False)
    top_left = db.Column(db.JSON, nullable=False)
    bottom_right = db.Column(db.JSON, nullable=False)
    classification = db.Column(db.String(255), nullable=True)
    certainty = db.Column(db.Float, nullable=True)
    image = db.relationship('Image', backref='elements')
    is_leader = db.Column(db.Boolean, nullable=False, default=False)

    def as_dict(self):
        return {
            'id': self.id,
            'top_left': self.top_left,
            'bottom_right': self.bottom_right,
            'certainty': self.certainty,
            'classification': self.classification,
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
    data = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())
    user = db.relationship('User', backref='results')

    def as_dict(self):
        return {
            'id': self.id,
            'user': self.user.username,
            'image_id': self.images[0].id,
            'data': self.data,
            'timestamp': self.timestamp
        }


class Dataset(db.Model):
    __tablename__ = 'dataset'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())
    unfinished = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    user = db.relationship('User', backref='datasets')
    preprocessed = False

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'user': self.user.username,
            'unfinished': self.unfinished,
            'timestamp': self.timestamp,
            'images': [image.as_dict() for image in self.images]
        }
