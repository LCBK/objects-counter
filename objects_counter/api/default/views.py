import os
import time
import typing

import flask
from flask import request
from flask_restx import Resource, Namespace
from werkzeug.datastructures import FileStorage

api = Namespace('default', description='Default namespace')
process_parser = api.parser()
process_parser.add_argument('image', type=FileStorage, location='files')


@api.route('/is-alive')
class IsAlive(Resource):
    def get(self) -> typing.Any:
        return 'Flask is alive!'


@api.route('/version')
class Version(Resource):
    def get(self) -> typing.Any:
        return '0.1'


@api.route('/process')
class Process(Resource):
    @api.expect(process_parser)
    @api.response(201, "Image submitted successfully")
    @api.response(400, "No image provided")
    @api.response(413, "Payload too large")
    @api.response(415, "Unsupported type")
    def post(self) -> typing.Any:
        if 'image' not in request.files:
            print("XD!")
            return 'debil', 400
        image = request.files["image"]

        # save the received image to upload directory
        if not os.path.exists(flask.current_app.config["UPLOAD_FOLDER"]):
            print("WARN: upload folder does not exist")
            os.makedirs(flask.current_app.config["UPLOAD_FOLDER"])
        dst = os.path.join(flask.current_app.config["UPLOAD_FOLDER"], image.filename)
        image.save(dst)

        # TODO: save file location in the db

        # TODO: submit the file for processing and wait for result

        # TODO: save the result to the db

        time.sleep(3)  # mocking processing time, TODO: remove

        mock_response = {
            "id": 123456,
            "data": [
                {
                    "top_left": [21, 5],
                    "bottom_right": [84, 67],
                    "certainty": 0.98,
                    "class": "lorem"
                },
                {
                    "top_left": [124, 5],
                    "bottom_right": [153, 80],
                    "certainty": 0.76,
                    "class": "ipsum"
                }
            ]
        }

        return mock_response, 201
