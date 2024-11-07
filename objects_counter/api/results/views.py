import base64
import logging
import typing

from flask import Response, jsonify, request
from flask_restx import Namespace, Resource
from werkzeug.exceptions import NotFound, Forbidden

from objects_counter.api.default.views import object_grouper
from objects_counter.api.utils import authentication_required
from objects_counter.db.dataops.dataset import get_dataset_by_id
from objects_counter.db.dataops.image import get_image_by_id, serialize_image_as_result
from objects_counter.db.dataops.result import get_result_by_id
from objects_counter.db.dataops.result import (get_user_results_serialized, get_user_results,
                                               rename_classification, delete_result_by_id)
from objects_counter.db.models import User

api = Namespace('results', description='Results related operations')
log = logging.getLogger(__name__)
# pylint: disable=too-few-public-methods, broad-exception-caught


@api.route('/')
class GetResults(Resource):
    @authentication_required
    def get(self, current_user: User) -> typing.Any:
        return jsonify(get_user_results_serialized(current_user))


@api.route('/thumbnails')
class GetThumbnails(Resource):
    @authentication_required
    def get(self, current_user: User) -> typing.Any:
        results = get_user_results(current_user)
        thumbnails = []
        for result in results:
            with open(result.image.thumbnail, 'rb') as thumbnail:
                base64_thumbnail = base64.b64encode(thumbnail.read())

            thumbnails.append({
                'id': result.id,
                'thumbnail': base64_thumbnail.decode('utf-8')
            })
        return jsonify(thumbnails)


@api.route('/<int:result_id>')
class Result(Resource):
    @api.doc(params={'result_id': 'The result ID'})
    @authentication_required
    def get(self, current_user: User, result_id: int) -> typing.Any:
        try:
            result_id = int(result_id)
            if result_id < 0:
                log.error("Invalid result ID: %s", result_id)
                raise ValueError("ID must be a positive integer")
            result = get_result_by_id(result_id)
            if result.user_id != current_user.id:
                return Response('Unauthorized', 403)
            return jsonify(result.as_dict())
        except ValueError as e:
            log.exception("Invalid result ID: %s", e)
            return Response("Invalid result ID", 400)
        except NotFound as e:
            log.exception("Result %s not found: %s", result_id, e)
            return Response(f"Result {result_id} not found", 404)
        except Exception as e:
            log.exception("Failed to get result %s: %s", result_id, e)
            return Response("Failed to get requested result", 500)

    @api.doc(params={'result_id': 'The result ID'})
    @authentication_required
    def delete(self, current_user: User, result_id: int) -> typing.Any:
        try:
            result_id = int(result_id)
            if result_id < 0:
                log.error("Invalid result ID: %s", result_id)
                raise ValueError("ID must be a positive integer")
            delete_result_by_id(result_id, current_user)
            return Response(status=204)
        except ValueError as e:
            log.exception("Invalid result ID: %s", e)
            return Response("Invalid result ID", 400)
        except Forbidden as e:
            log.exception("Failed to delete result %s: %s", result_id, e)
            return Response("Forbidden", 403)
        except NotFound as e:
            log.exception("Result %s not found: %s", result_id, e)
            return Response("Result not found", 404)
        except Exception as e:
            log.exception("Failed to delete result %s: %s", result_id, e)
            return Response("Failed to delete result", 500)


@api.route('/<int:result_id>/classification/<string:classification>/rename')
class RenameClassification(Resource):
    @api.doc(params={'result_id': 'The result ID', 'classification': 'The classification to rename'})
    @authentication_required
    def post(self, current_user: User, result_id: int, classification: str) -> typing.Any:
        new_classification = request.get_data(as_text=True)
        result_id = int(result_id)
        if result_id < 0:
            return Response('Invalid result ID', 400)
        try:
            count = rename_classification(current_user, result_id, classification, new_classification)
            return Response(f"{count}", 200)
        except ValueError as e:
            log.exception("Failed to rename classification %s in result %s: %s", classification, result_id, e)
            return Response("Invalid classification name", 400)
        except Forbidden as e:
            log.exception("Failed to rename classification %s in result %s: %s", classification, result_id, e)
            return Response("Unauthorized", 403)
        except NotFound as e:
            log.exception("Failed to rename classification %s in result %s: %s", classification, result_id, e)
            return Response("Result not found", 404)
        except Exception as e:
            log.exception("Failed to rename classification %s in result %s: %s", classification, result_id, e)
            return Response("Failed to rename classification", 500)


@api.route('/<int:result_id>/compare/<int:dataset_id>')
class CompareResults(Resource):
    @authentication_required
    def get(self, current_user: User, result_id: int, dataset_id: int) -> typing.Any:
        try:
            result = get_result_by_id(int(result_id))
            image = get_image_by_id(result.image_id)
            dataset = get_dataset_by_id(int(dataset_id))
            if result.user_id != dataset.user_id or dataset.user_id != current_user.id:
                log.error("User %s is not authorized to compare result %s with dataset %s",
                          current_user, result_id, dataset_id)
                return Response('Unauthorized', 403)
            object_grouper.assign_dataset_categories_to_objects(image, dataset)
            return jsonify(serialize_image_as_result(image))
        except ValueError as e:
            log.exception("Failed to compare results: %s", e)
            return Response("Invalid result or dataset ID", 400)
        except NotFound as e:
            log.exception("Failed to compare results: %s", e)
            return Response("Result or dataset not found", 404)
        except Exception as e:
            log.exception("Failed to compare results: %s", e)
            return Response("Failed to compare results", 500)
