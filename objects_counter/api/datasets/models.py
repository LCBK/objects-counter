from flask_restx import fields

from objects_counter.api.common import api

classification_model = api.model('Classification', {
    'name': fields.String(required=True, description='The classification name'),
    'leader': fields.Integer(required=True, description='The leader ID')
})

insert_dataset_model = api.model('NewDataset', {
    'name': fields.String(required=True, description='The dataset name'),
    'unfinished': fields.Boolean(required=False, description='Whether the dataset is unfinished')
})

insert_image_model = api.model('NewDataset', {
    'image_id': fields.Integer(required=True, description='The image ID'),
    'classifications': fields.List(fields.Nested(classification_model), required=True,
                                   description='List of classifications'),
})

patch_dataset_model = api.model('PatchDataset', {
    'name': fields.String(required=False, description='The new dataset name'),
    'unfinished': fields.Boolean(required=False, description='Whether the dataset is unfinished')
})

adjust_classification_model = api.model('AdjustClassification', {
    "name": fields.String(required=True, description='The classification name'),
    "elements": fields.List(fields.Integer, required=True, description='List of element IDs'),
})

adjust_classifications_model = api.model('AdjustClassifications', {
    "classifications": fields.List(fields.Nested(adjust_classification_model), required=True,
                                   description='List of classifications'),
})

images_list_model = api.model('ImagesList', {
    "image_ids": fields.List(fields.Integer, required=True, description='List of image IDs'),
})
