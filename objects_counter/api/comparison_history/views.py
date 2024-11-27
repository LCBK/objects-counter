import logging
import typing

from flask import jsonify
from flask_restx import Namespace, Resource

from objects_counter.api.utils import authentication_required, get_thumbnails
from objects_counter.db.dataops.comparison_history import get_comparisons_by_user_id
from objects_counter.db.models import User

api = Namespace('comparison_history', description='History of comparisons (image to dataset)')
log = logging.getLogger(__name__)

# pylint: disable=broad-exception-caught


@api.route('/')
class ComparisonHistory(Resource):
    @api.doc("List user's comparisons")
    @api.response(200, 'Success')
    @api.response(401, 'You must be logged in to access this resource')
    @api.response(403, 'You are not authorized to access this resource')
    @api.response(500, 'Failed to list comparisons')
    @authentication_required
    def get(self, current_user: User) -> typing.Any:
        """List all user's comparisons"""
        return jsonify(get_comparisons_by_user_id(current_user.id))


@api.route('/thumbnails')
class ComparisonHistoryThumbnails(Resource):
    @api.doc("Get user's comparisons thumbnails")
    @api.response(200, 'Success')
    @api.response(401, 'You must be logged in to access this resource')
    @api.response(403, 'You are not authorized to access this resource')
    @api.response(500, 'Failed to list comparisons')
    @authentication_required
    def get(self, current_user: User) -> typing.Any:
        """List user's comparisons thumbnails"""
        comparisons = current_user.comparisons
        thumbnails = get_thumbnails(comparisons)
        return jsonify(thumbnails)
