from flask_restx import fields
from objects_counter.api import api

submit = api.model('Submit', {
    'threshold': fields.Float(required=True, description='The threshold to use'),
    'min_size': fields.Integer(required=True, description='The minimum size of objects to count'),
    'max_size': fields.Integer(required=True, description='The maximum size of objects to count'),
})
