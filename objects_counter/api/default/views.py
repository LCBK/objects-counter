import json
import os
import random
import string
import time
import typing

import cv2
import flask
from flask import request
from flask_restx import Resource, Namespace
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from image_segmentation.segment_anything_object_counter import SegmentAnythingObjectCounter
from objects_counter.api.default.models import points_model
from objects_counter.api.utils import authentication_optional
from objects_counter.consts import SAM_CHECKPOINT
from objects_counter.db.dataops.image import insert_image
from objects_counter.db.models import User

api = Namespace('default', description='Default namespace')
process_parser = api.parser()
process_parser.add_argument('image', type=FileStorage, location='files')
sam = SegmentAnythingObjectCounter(SAM_CHECKPOINT)

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
            print("ERROR: no image provided")
            return 'No image provided', 400
        image = request.files["image"]

        # save the received image to upload directory
        if not os.path.exists(flask.current_app.config["UPLOAD_FOLDER"]):
            print("WARN: upload folder does not exist")
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
        # TODO: pass image_obj to the sam object, use models.Image in sam instead of index
        image_content = cv2.imread(image_obj.filepath)
        index = sam.add_image(image_content)
        return index, 201


@api.route('/images/<int:image_id>/background')
class BackgroundPoints(Resource):
    @api.doc(params={'image_id': 'The image ID'})
    @api.expect(points_model)
    def put(self, image_id: int) -> typing.Any:
        points = request.json
        if not points:
            print("ERROR: no points provided")
            return 'No points provided', 400
        if not isinstance(points, dict):
            print("ERROR: points should be a dictionary")
            return 'Points should be a dictionary', 400

        # save the points in the db
        sam.calculate_image_mask(image_id, points["data"])
        mask = sam.get_image_mask(image_id).tolist()
        result = {
            "mask": mask
        }
        return json.dumps(result), 200


@api.route('/images/<int:image_id>/background/accept')
class AcceptBackgroundPoints(Resource):
    @api.doc(params={'image_id': 'The image ID'})
    @authentication_optional
    def post(self, current_user: User, image_id: int) -> typing.Any:
        result = sam.get_object_count(image_id)
        response = {}
        if not result:
            print("ERROR: no result received")
            return 'Error processing image', 500
        response["id"] = image_id
        response["data"] = []
        for obj in result[1]:
            response["data"].append({
                "top_left": obj[0],
                "bottom_right": obj[1],
                "certainty": 1.0,
                "class": "NotImplemented"
            })

        if current_user:
            # user_id = current_user.id
            # insert_result(user_id, image_obj.id, result)
            return json.dumps(response), 201
        return json.dumps(response), 200
