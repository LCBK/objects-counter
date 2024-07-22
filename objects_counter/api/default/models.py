from flask_restx import fields

from objects_counter.api.common import api

points_model = api.model('Points', {
    'data': fields.List(fields.List(fields.Integer), required=True, description='List of points [x, y]'),
})
