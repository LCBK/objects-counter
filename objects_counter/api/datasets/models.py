from flask_restx import fields

from objects_counter.api.common import api

classification_model = api.model('Classification', {
    'name': fields.String(required=True, description='The classification name'),
    'leader': fields.Integer(required=True, description='The leader ID')
})

insert_dataset_model = api.model('NewDataset', {
    'name': fields.String(required=True, description='The dataset name')
})

insert_image_model = api.model('NewDataset', {
    'image_id': fields.Integer(required=True, description='The image ID'),
    'classifications': fields.List(fields.Nested(classification_model), required=True,
                                   description='List of classifications'),
})

rename_dataset_model = api.model('RenameDataset', {
    'name': fields.String(required=True, description='The new dataset name'),
})

adjust_classification_model = api.model('AdjustClassification', {
    "name": fields.String(required=True, description='The classification name'),
    "elements": fields.List(fields.Integer, required=True, description='List of element IDs'),
})

adjust_classifications_model = api.model('AdjustClassifications', {
    "classifications": fields.List(fields.Nested(adjust_classification_model), required=True,
                                   description='List of classifications'),
})
