import json
import logging
import os
import random
import string
import time
import typing

import flask
from flask import request, send_file, Response, jsonify
from flask_restx import Resource, Namespace
from werkzeug.datastructures import FileStorage
from werkzeug.exceptions import NotFound
from werkzeug.utils import secure_filename

from image_segmentation.object_classification.classifier import ObjectClassifier
from image_segmentation.object_classification.comparison import find_missing_elements
from image_segmentation.object_classification.feature_extraction import FeatureSimilarity, ColorSimilarity
from image_segmentation.object_detection.object_segmentation import ObjectSegmentation
from objects_counter.api.default.models import points_model, accept_model
from objects_counter.api.utils import authentication_optional, authentication_required, gzip_compress
from objects_counter.consts import SAM_CHECKPOINT, SAM_MODEL_TYPE
from objects_counter.db.dataops.image import insert_image, update_background_points, get_image_by_id, \
    serialize_image_as_result, set_element_as_leader
from objects_counter.db.dataops.result import insert_result
from objects_counter.db.models import User
from objects_counter.utils import create_thumbnail


api = Namespace('default', description='Default namespace')
process_parser = api.parser()
process_parser.add_argument('image', type=FileStorage, location='files')
sam = ObjectSegmentation(SAM_CHECKPOINT, model_type=SAM_MODEL_TYPE)
feature_similarity_model = FeatureSimilarity()
color_similarity_model = ColorSimilarity()
object_grouper = ObjectClassifier(sam, feature_similarity_model, color_similarity_model)

log = logging.getLogger(__name__)


@api.route('/is-alive')
class IsAlive(Resource):
    def get(self) -> typing.Any:
        return 'Flask is alive!'


@api.route('/version')
class Version(Resource):
    def get(self) -> typing.Any:
        return '0.1'


@api.route('/images/upload')
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

        thumbnail_path = os.path.join(flask.current_app.config["THUMBNAIL_FOLDER"], unique_safe_filename)
        create_thumbnail(dst, thumbnail_path)

        # save file location in the db
        image_obj = insert_image(dst, thumbnail_path)
        _ = sam.calculate_mask(image_obj)
        return image_obj.id, 201


@api.route('/images/<int:image_id>')
class ImageApi(Resource):
    @api.doc(params={'image_id': 'The image ID'})
    @api.response(200, "Image found")
    @api.response(401, "Unauthorized")
    @api.response(403, "Forbidden")
    @api.response(404, "Image not found")
    @authentication_required
    def get(self, current_user: User, image_id: int) -> typing.Any:
        try:
            image = get_image_by_id(image_id)
            if image.result.user_id != current_user.id:
                log.error("User %s is not authorized to access image %s", current_user.id, image_id)
                return 'Forbidden', 403
        except NotFound as e:
            log.exception("Image %s not found: %s", image_id, e)
            return 'Image not found', 404
        return send_file(image.filepath)


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
        result_bytes = json.dumps(result).encode('utf-8')
        compressed_result = gzip_compress(result_bytes)
        return Response(compressed_result, 200, headers={'Content-Encoding': 'gzip'}, content_type='application/json')


@api.route('/images/<int:image_id>/background/accept')
class AcceptBackgroundPoints(Resource):
    @api.doc(params={'image_id': 'The image ID'})
    @api.expect(accept_model)
    @api.response(200, "Objects counted")
    @api.response(201, "Objects counted and results saved")
    @api.response(404, "Image not found")
    @api.response(500, "Error processing image")
    @authentication_optional
    def post(self, current_user: User, image_id: int) -> typing.Any:
        as_dataset = request.json.get('as_dataset', False)
        try:
            image = get_image_by_id(image_id)
        except NotFound as e:
            log.exception("Image %s not found: %s", image_id, e)
            return 'Image not found', 404

        sam.count_objects(image)

        if not as_dataset:
            object_grouper.group_objects_by_similarity(image)
            response = serialize_image_as_result(image)
        else:
            if not current_user:
                log.error("User must be logged in")
                return Response('You must be logged in', 401)
            return jsonify(image.as_dict())

        if current_user:
            user_id = current_user.id
            result = insert_result(user_id, image.id, response)
            response["id"] = result.id
            return json.dumps(response), 201
        return json.dumps(response), 200


@api.route('/images/<int:image_id>/classify-by-leaders')
class ClassifyByLeaders(Resource):
    @api.doc(params={'image_id': 'The image ID'})
    @api.response(200, "Objects classified")
    @api.response(404, "Image not found")
    @api.response(500, "Error processing image")
    def post(self, image_id: int) -> typing.Any:
        data = request.json
        leaders = data.get("leaders", [])
        try:
            image = get_image_by_id(image_id)
            for leader in leaders:
                set_element_as_leader(leader, image)
        except NotFound as e:
            log.exception("Image %s not found: %s", image_id, e)
            return Response('Image not found', 404)
        except ValueError as e:
            log.exception("Invalid leader ID: %s", e)
            return Response(f'One or more leaders do not belong to the image {image_id}', 400)

        object_grouper.assign_categories_by_representatives(image)
        return Response(json.dumps(serialize_image_as_result(image)), 200)


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

        result = find_missing_elements(first_image, second_image, object_grouper)

        response = {
            "first_count": len(first_image.elements),
            "second_count": len(second_image.elements),
            "result": result
        }

        return json.dumps(response), 200
