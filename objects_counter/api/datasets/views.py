import logging
import typing

from flask import jsonify, Response, request
from flask_restx import Namespace, Resource
from natsort import natsorted
from werkzeug.exceptions import NotFound, Forbidden

from objects_counter.api.datasets.models import insert_dataset_model, insert_image_model, patch_dataset_model, \
    adjust_classifications_model, images_list_model
from objects_counter.api.default.views import object_grouper
from objects_counter.api.utils import authentication_required, get_thumbnails
from objects_counter.db.dataops.comparison_history import insert_comparison
from objects_counter.db.dataops.dataset import get_user_datasets_serialized, get_dataset_by_id, delete_dataset_by_id, \
    insert_dataset, add_image_to_dataset, rename_dataset, get_user_datasets, update_unfinished_state
from objects_counter.db.dataops.image import serialize_image_as_result, get_image_by_id, \
    bulk_update_element_classification_by_id
from objects_counter.db.models import User

api = Namespace('datasets', description='Datasets related operations')
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
            name = data.get('name')
            unfinished = data.get('unfinished', False)
            if not name:
                raise ValueError("Missing required fields")
            dataset = insert_dataset(current_user.id, name, unfinished)
            return Response(str(dataset.id), 201)
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
            dataset_dict = {
                "id": dataset.id,
                "name": dataset.name,
                "images": []
            }
            for image in dataset.images:
                image_dict = serialize_image_as_result(image)
                image_dict["id"] = image.id
                dataset_dict['images'].append(image_dict)
            return jsonify(dataset_dict)
        except ValueError as e:
            log.exception("Invalid dataset ID: %s", e)
            return Response("Invalid dataset ID", 400)
        except NotFound as e:
            log.exception("Dataset not found: %s", e)
            return Response("Dataset not found", 404)

    @api.expect(patch_dataset_model)
    @authentication_required
    def patch(self, current_user: User, dataset_id: int) -> typing.Any:
        data = request.json
        name = data.get('name', '')
        unfinished = data.get('unfinished', None)
        if not name and unfinished is None:
            log.error("No data provided for dataset update")
            return Response("No data provided for dataset update", 400)
        try:
            if name:
                dataset = rename_dataset(dataset_id, name, current_user)
            if unfinished is not None:
                dataset = update_unfinished_state(dataset_id, unfinished, current_user)
            return jsonify(dataset.as_dict())  # pylint: disable=possibly-used-before-assignment # false positive
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
            classifications = data.get('classifications', [])
            if not image_id or image_id < 0:
                raise ValueError("Invalid image ID")
            if not classifications:
                raise ValueError("No classifications provided")
            dataset = add_image_to_dataset(dataset, image_id, classifications, object_classifier=object_grouper)
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


@api.route('/<int:dataset_id>/images/<int:image_id>')
class AdjustClassifications(Resource):
    @api.expect(adjust_classifications_model)
    def patch(self, dataset_id: int, image_id: int) -> typing.Any:
        data = request.json
        try:
            dataset_id = int(dataset_id)
            image_id = int(image_id)
            if dataset_id < 0 or image_id < 0:
                log.error("Invalid dataset ID or image ID: %s, %s", dataset_id, image_id)
                raise ValueError("ID must be a positive integer")
            dataset = get_dataset_by_id(dataset_id)
            image = get_image_by_id(image_id)
            if image.dataset_id != dataset.id:
                log.error("Image %s does not belong to dataset %s", image_id, dataset_id)
                return Response("Image does not belong to dataset", 400)
            classifications = data.get('classifications', [])
            bulk_update_element_classification_by_id(classifications)
            return Response(serialize_image_as_result(image), 200)
        except ValueError as e:
            log.exception("Invalid dataset ID %s or image ID %s: %s", dataset_id, image_id, e)
            return Response("Invalid dataset ID or image ID", 400)
        except NotFound as e:
            log.exception("Dataset or image not found: %s", e)
            return Response("Dataset or image not found", 404)
        except Exception as e:
            log.exception("Failed to adjust classifications: %s", e)
            return Response("Failed to adjust classifications", 500)


@api.route('/<int:dataset_id>/comparison')
class CompareImageToDataset(Resource):
    @api.expect(images_list_model)
    @api.response(200, "Comparison successful")
    @api.response(400, "Invalid image or dataset ID")
    @api.response(401, "You must be logged in")
    @api.response(403, "You are not authorized to access that dataset")
    @api.response(404, "Image or dataset not found")
    @api.response(500, "Error while comparing images with dataset")
    @authentication_required
    def post(self, current_user: User, dataset_id: int) -> typing.Any:
        data = request.json
        image_ids = data.get('image_ids', [])
        try:
            dataset_id = int(dataset_id)
            for image_id in image_ids:
                image_id = int(image_id)
                if image_id < 0:
                    log.error("Invalid image ID: %s", image_id)
                    raise ValueError("ID must be a positive integer")
        except (ValueError, TypeError) as e:
            log.exception("Invalid ID: %s", e)
            return Response("Invalid image or dataset ID", 400)
        try:
            dataset = get_dataset_by_id(dataset_id)
            if dataset.user_id != current_user.id:
                log.error("User %s is not authorized to access dataset %s", current_user, dataset_id)
                return Response('You are not authorized to access that dataset', 403)
            images = []
            for image_id in image_ids:
                images.append(get_image_by_id(image_id))
            diff = object_grouper.classify_images_based_on_dataset(images, dataset)
            comparison = insert_comparison(current_user, dataset, images, diff)
            return jsonify(comparison.as_dict())
        except NotFound as e:
            log.exception("Image or dataset not found: %s", e)
            return Response("Image or dataset not found", 404)
        except Exception as e:
            log.exception("Error while comparing images with dataset: %s", e)
            return Response("Error while comparing images with dataset", 500)


@api.route('/thumbnails')
class DatasetsThumbnails(Resource):
    @authentication_required
    def get(self, current_user: User) -> typing.Any:
        datasets = get_user_datasets(current_user)
        thumbnails = get_thumbnails(datasets)
        return jsonify(thumbnails)
