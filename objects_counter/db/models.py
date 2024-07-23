from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

# pylint: disable=too-few-public-methods

class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filepath = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=db.func.now())


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
    image = db.relationship('Image', backref='results')

    def as_dict(self):
        return {
            'id': self.id,
            'user': self.user.username,
            'image_id': self.image_id,
            'data': self.data,
            'timestamp': self.timestamp
        }
