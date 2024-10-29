import logging
import typing

from flask import jsonify, Response, request
from flask_restx import Namespace, Resource
from werkzeug.exceptions import NotFound, Forbidden

from objects_counter.api.datasets.models import insert_dataset_model, insert_image_model, rename_dataset_model
from objects_counter.api.utils import authentication_required
from objects_counter.db.dataops.dataset import get_user_datasets_serialized, get_dataset_by_id, delete_dataset_by_id, \
    insert_dataset, add_image_to_dataset, rename_dataset
from objects_counter.db.models import User

api = Namespace('results', description='Results related operations')
log = logging.getLogger(__name__)

# pylint: disable=broad-exception-caught


@api.route('/')
class Datasets(Resource):
    @authentication_required
    def get(self, current_user: User) -> typing.Any:
        return jsonify(get_user_datasets_serialized(current_user))

    @api.expect(insert_dataset_model)
    @authentication_required
    def post(self, current_user: User) -> typing.Any:
        data = request.json
        try:
            image_id = data.get('image_id')
            name = data.get('name')
            if not image_id or not name:
                raise ValueError("Missing required fields")
            dataset = insert_dataset(current_user.id, image_id, name)
            return jsonify(dataset.as_dict())
        except ValueError as e:
            log.exception("Invalid dataset data: %s", e)
            return Response("Invalid dataset data", 400)


@api.route('/<int:dataset_id>')
class Dataset(Resource):
    @authentication_required
    def get(self, current_user: User, dataset_id: int) -> typing.Any:
        try:
            dataset_id = int(dataset_id)
            if dataset_id < 0:
                log.error("Invalid dataset ID: %s", dataset_id)
                raise ValueError("ID must be a positive integer")
            dataset = get_dataset_by_id(dataset_id)
            if dataset.user_id != current_user.id:
                log.error("User %s is not authorized to access dataset %s", current_user, dataset_id)
                return Response('Unauthorized', 403)
            return jsonify(dataset.as_dict())
        except ValueError as e:
            log.exception("Invalid dataset ID: %s", e)
            return Response("Invalid dataset ID", 400)
        except NotFound as e:
            log.exception("Dataset not found: %s", e)
            return Response("Dataset not found", 404)

    @api.expect(rename_dataset_model)
    @authentication_required
    def patch(self, current_user: User, dataset_id: int) -> typing.Any:
        data = request.json
        name = data.get('name')
        try:
            dataset = rename_dataset(dataset_id, name, current_user)
            return jsonify(dataset.as_dict())
        except Forbidden as e:
            log.exception("User %s is not authorized to rename dataset %s: %s", current_user, dataset_id, e)
            return Response("You are not authorized to rename this dataset", 403)
        except NotFound as e:
            log.exception("Dataset not found: %s", e)
            return Response("Dataset not found", 404)
        except ValueError as e:
            log.exception("Invalid dataset name: %s", e)
            return Response("Invalid dataset name", 400)
        except Exception as e:
            log.exception("Failed to rename dataset: %s", e)
            return Response("Failed to rename dataset", 500)

    @authentication_required
    def delete(self, current_user: User, dataset_id: int) -> typing.Any:
        try:
            dataset_id = int(dataset_id)
            if dataset_id < 0:
                log.error("Invalid dataset ID: %s", dataset_id)
                raise ValueError("ID must be a positive integer")
            delete_dataset_by_id(dataset_id, current_user)
            return Response(status=204)
        except ValueError as e:
            log.exception("Invalid dataset ID: %s", e)
            return Response("Invalid dataset ID", 400)
        except Forbidden as e:
            log.exception("User %s is not authorized to delete dataset %s: %s", current_user, dataset_id, e)
            return Response("You are not authorized to delete this dataset", 403)
        except NotFound as e:
            log.exception("Dataset not found: %s", e)
            return Response("Dataset not found", 404)
        except Exception as e:
            log.exception("Failed to delete dataset: %s", e)
            return Response("Failed to delete dataset", 500)


@api.route('/<int:dataset_id>/images')
class DatasetImages(Resource):
    @authentication_required
    def get(self, current_user: User, dataset_id: int) -> typing.Any:
        images = []
        try:
            dataset_id = int(dataset_id)
            if dataset_id < 0:
                log.error("Invalid dataset ID: %s", dataset_id)
                raise ValueError("ID must be a positive integer")
        except ValueError as e:
            log.exception("Invalid dataset ID: %s", e)
            return Response("Invalid dataset ID", 400)
        dataset = get_dataset_by_id(dataset_id)
        if dataset.user_id != current_user.id:
            return Response('Unauthorized', 403)
        for image in dataset.images:
            images.append(image.as_dict())
        return jsonify(images)

    @api.expect(insert_image_model)
    @authentication_required
    def post(self, current_user: User, dataset_id: int) -> typing.Any:
        data = request.json
        try:
            dataset_id = int(dataset_id)
            if dataset_id < 0:
                log.error("Invalid dataset ID: %s", dataset_id)
                raise ValueError("ID must be a positive integer")
            dataset = get_dataset_by_id(dataset_id)
            if dataset.user_id != current_user.id:
                log.error("User %s is not authorized to add images to dataset %s", current_user, dataset_id)
                return Response("You are not authorized to add images to dataset {dataset_id}", 403)
            image_id = int(data.get('image_id'))
            if not image_id or image_id < 0:
                raise ValueError("Invalid image ID")
            dataset = add_image_to_dataset(dataset_id, image_id)
            return jsonify(dataset.as_dict())
        except ValueError as e:
            log.exception("Invalid dataset ID: %s", e)
            return Response("Invalid dataset ID", 400)
        except Forbidden as e:
            log.exception("User %s is not authorized to add image to dataset %s: %s",
                          current_user, dataset_id, e)
            return Response("You are not authorized to add specified image to this dataset", 403)
        except NotFound as e:
            log.exception("Dataset not found: %s", e)
            return Response("Dataset not found", 404)
        except Exception as e:
            log.exception("Failed to add image to dataset: %s", e)
            return Response("Failed to add image to dataset", 500)
