from flask_restx import fields

from objects_counter.api.common import api

point_model = api.model('Point', {
    'position': fields.List(fields.Integer, required=True, description='Position of the point [x, y]'),
    'positive': fields.Boolean(required=True, description='Positive or negative point'),
})

points_model = api.model('Points', {
    'data': fields.List(fields.Nested(point_model), required=True, description='List of points [x, y]'),
})

accept_model = api.model('Accept', {
    'skip_classification': fields.Boolean(required=False, description='Skip classification', default=False),
})
