from flask_restx import fields

from objects_counter.api.common import api

insert_result_model = api.model('InsertResult', {
    'image_ids': fields.List(fields.Integer, required=True, description='The image IDs'),
    'leaders': fields.List(fields.Integer, required=False, description='The leader element IDs')
})
