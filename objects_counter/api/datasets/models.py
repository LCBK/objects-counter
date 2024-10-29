from flask_restx import fields

from objects_counter.api.common import api

classification_model = api.model('Classification', {
    'name': fields.String(required=True, description='The classification name'),
    'elements': fields.List(fields.Integer, required=True, description='List of element IDs'),
})

insert_dataset_model = api.model('NewDataset', {
    'image_id': fields.Integer(required=True, description='The image ID'),
    'name': fields.String(required=True, description='The dataset name'),
    'classifications': fields.List(fields.Nested(classification_model), required=True,
                                   description='List of classifications'),
})

insert_image_model = api.model('NewImage', {
    'image_id': fields.Integer(required=True, description='The image ID'),
})

rename_dataset_model = api.model('RenameDataset', {
    'name': fields.String(required=True, description='The new dataset name'),
})
