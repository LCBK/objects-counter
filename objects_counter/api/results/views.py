import logging
import typing

from flask import Response, jsonify, request
from flask_restx import Namespace, Resource
from werkzeug.exceptions import NotFound, Forbidden

from objects_counter.api.default.views import object_grouper
from objects_counter.api.results.models import insert_result_model
from objects_counter.api.utils import authentication_required, get_thumbnails, authentication_optional
from objects_counter.db.dataops.dataset import get_dataset_by_id
from objects_counter.db.dataops.image import serialize_image_as_result, get_images_by_ids
from objects_counter.db.dataops.result import get_result_by_id, insert_result
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

    @api.expect(insert_result_model)
    @authentication_optional
    def post(self, current_user: User | None) -> typing.Any:
        try:
            data = request.get_json()
            automatic = data.get('automatic', None)
            image_ids = data.get('image_ids', [])
            leaders = data.get('leaders', [])

            if automatic is None:
                raise ValueError("Automatic field must be provided")
            if not image_ids:
                raise ValueError("Image IDs must be provided")
            if not automatic:
                if not leaders:
                    raise ValueError("Leaders must be provided")

            images = get_images_by_ids(image_ids)

            if automatic:
                object_grouper.group_objects_by_similarity(images)
            else:
                # TODO
                return Response("Manual classification is not supported yet", 501)

            result = insert_result(current_user, images, {})

            return jsonify(result.as_dict())
        except ValueError as e:
            log.exception("Failed to insert result: %s", e)
            return Response("Invalid data", 400)
        except Exception as e:
            log.exception("Failed to insert result: %s", e)
            return Response("Failed to insert result", 500)


@api.route('/thumbnails')
class GetThumbnails(Resource):
    @authentication_required
    def get(self, current_user: User) -> typing.Any:
        results = get_user_results(current_user)
        thumbnails = get_thumbnails(results)
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
            if result.user != current_user:
                return Response('Unauthorized', 403)
            return jsonify(result.as_dict())
        except ValueError as e:
            log.exception("Invalid result ID: %s", e)
            return Response("Invalid result ID", 400)
        except NotFound as e:
            log.exception("Result %s not found: %s", result_id, e)
            return Response("Result not found", 404)
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
        try:
            result_id = int(result_id)
            if result_id < 0:
                raise ValueError("ID must be a positive integer")
        except (ValueError, TypeError) as e:
            log.exception("Invalid result ID %s: %s", result_id, e)
            return Response("Invalid result ID", 400)
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
            image = result.images[0]
            dataset = get_dataset_by_id(int(dataset_id))
            if result.user != dataset.user or dataset.user != current_user:
                log.error("User %s is not authorized to compare result %s with dataset %s",
                          current_user, result_id, dataset_id)
                return Response('Unauthorized', 403)
            object_grouper.classify_images_based_on_dataset([image], dataset)
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
