from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Image(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filepath = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
