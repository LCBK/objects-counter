import json
import logging
import os
import random
import string
import time
import typing

import flask
from flask import request
from flask_restx import Resource, Namespace
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import NotFound
from werkzeug.utils import secure_filename

from image_segmentation.object_classification.classifier import ObjectClassifier
from image_segmentation.object_classification.comparison import compare_number_of_elements
from image_segmentation.object_classification.feature_extraction import CosineSimilarity
from image_segmentation.object_detection.object_segmentation import ObjectSegmentation
from objects_counter.api.default.models import points_model
from objects_counter.api.utils import authentication_optional
from objects_counter.consts import SAM_CHECKPOINT, SAM_MODEL_TYPE
from objects_counter.db.dataops.image import insert_image, update_background_points, get_image_by_id
from objects_counter.db.dataops.result import insert_result
from objects_counter.db.models import User

api = Namespace('default', description='Default namespace')
process_parser = api.parser()
process_parser.add_argument('image', type=FileStorage, location='files')
sam = ObjectSegmentation(SAM_CHECKPOINT, model_type=SAM_MODEL_TYPE)
similarity_model = CosineSimilarity()
object_grouper = ObjectClassifier(sam, similarity_model)

log = logging.getLogger(__name__)


@api.route('/is-alive')
class IsAlive(Resource):
    def get(self) -> typing.Any:
        return 'Flask is alive!'


@api.route('/version')
class Version(Resource):
    def get(self) -> typing.Any:
        return '0.1'


@api.route('/upload')
class Process(Resource):
    @api.expect(process_parser)
    @api.response(201, "Image submitted successfully")
    @api.response(400, "No image provided")
    @api.response(413, "Payload too large")
    @api.response(415, "Unsupported type")
    def post(self) -> typing.Any:
        if 'image' not in request.files:
            log.error("No image provided")
            return 'No image provided', 400
        image = request.files["image"]

        # save the received image to upload directory
        if not os.path.exists(flask.current_app.config["UPLOAD_FOLDER"]):
            log.warning("Upload folder does not exist")
            os.makedirs(flask.current_app.config["UPLOAD_FOLDER"])
        filename = secure_filename(image.filename)
        if not filename:
            filename = "empty_filename"
        prefix = (str(int(time.time())) + "_").join(random.choice(string.ascii_letters) for _ in range(8))
        unique_safe_filename = prefix + "_" + filename
        dst = os.path.join(flask.current_app.config["UPLOAD_FOLDER"], unique_safe_filename)
        image.save(dst)

        # save file location in the db
        image_obj = insert_image(dst)
        return image_obj.id, 201


@api.route('/images/<int:image_id>/background')
class BackgroundPoints(Resource):
    @api.doc(params={'image_id': 'The image ID'})
    @api.response(200, "Background points updated")
    @api.response(400, "No points provided")
    @api.response(404, "Image not found")
    @api.expect(points_model)
    def put(self, image_id: int) -> typing.Any:
        points = request.json
        if not points:
            log.error("No points provided")
            return 'No points provided', 400
        if not isinstance(points, dict):
            log.error("Points should be a dictionary")
            return 'Points should be a dictionary', 400
        try:
            image = get_image_by_id(image_id)
        except NotFound as e:
            log.exception("Image %s not found: %s", image_id, e)
            return 'Image not found', 404

        # save the points in the db
        update_background_points(image_id, points)
        mask = sam.calculate_mask(image).tolist()
        result = {"mask": mask}
        return json.dumps(result), 200


@api.route('/images/<int:image_id>/background/accept')
class AcceptBackgroundPoints(Resource):
    @api.doc(params={'image_id': 'The image ID'})
    @api.response(200, "Objects counted")
    @api.response(201, "Objects counted and results saved")
    @api.response(404, "Image not found")
    @api.response(500, "Error processing image")
    @authentication_optional
    def post(self, current_user: User, image_id: int) -> typing.Any:
        try:
            image = get_image_by_id(image_id)
        except NotFound as e:
            log.exception("Image %s not found: %s", image_id, e)
            return 'Image not found', 404

        sam.count_objects(image)

        object_grouper.group_objects_by_similarity(image)

        response = {
            "count": len(image.elements),
            "classifications": []
        }

        classification_dict = {}

        for element in image.elements:
            element_data = element.as_dict()

            element_data["certainty"] = round(element.certainty, 2)

            if element.classification not in classification_dict:
                classification_dict[element.classification] = {
                    "classification": element.classification,
                    "objects": []
                }

            classification_dict[element.classification]["objects"].append(element_data)

        response["classifications"] = list(classification_dict.values())

        if current_user:
            user_id = current_user.id
            insert_result(user_id, image.id, response)
            return json.dumps(response), 201
        return json.dumps(response), 200

# Temporary, to change in the future
@api.route('/images/compare')
class CompareImageElements(Resource):
    @api.doc(params={'image_id': 'The image ID'})
    @api.response(200, "Elements compared")
    @api.response(404, "Image not found")
    def post(self):
        first_image_id = request.json["first_image_id"]
        second_image_id = request.json["second_image_id"]

        try:
            first_image = get_image_by_id(first_image_id)
        except NotFound as e:
            log.exception("Image %s not found: %s", first_image_id, e)
            return 'Image not found', 404

        try:
            second_image = get_image_by_id(second_image_id)
        except NotFound as e:
            log.exception("Image %s not found: %s", second_image_id, e)
            return 'Image not found', 404

        result = compare_number_of_elements(first_image, second_image)

        response = {
            "first_count": len(first_image.elements),
            "second_count": len(second_image.elements),
            "result": result
        }

        return json.dumps(response), 200
