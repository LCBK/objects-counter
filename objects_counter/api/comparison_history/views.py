import logging
import typing

from flask import jsonify, Response
from flask_restx import Namespace, Resource
from werkzeug.exceptions import Forbidden, NotFound

from objects_counter.api.utils import authentication_required, get_thumbnails
from objects_counter.db.dataops.comparison_history import get_comparisons_by_user_id, delete_comparison_by_id, \
    get_comparison_by_id
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


@api.route('/<int:comparison_id>')
class ComparisonHistoryDetails(Resource):
    @api.doc("Get comparison details")
    @api.response(200, 'Success')
    @api.response(401, 'You must be logged in to access this resource')
    @api.response(403, 'You are not authorized to access this resource')
    @api.response(404, 'Comparison not found')
    @api.response(500, 'Failed to get comparison')
    @authentication_required
    def get(self, current_user: User, comparison_id: int) -> typing.Any:
        """Get comparison details"""
        comparison = get_comparison_by_id(comparison_id)
        if comparison.user_id != current_user.id:
            log.error('User %s is not authorized to access comparison %s', current_user, comparison_id)
            return Response('You are not authorized to access this comparison', 403)
        if not comparison:
            log.error('Comparison %s not found', comparison_id)
            return Response('Comparison not found', 404)
        return jsonify(comparison.as_dict())

    @api.doc("Delete comparison")
    @api.response(204, 'Comparison deleted')
    @api.response(401, 'You must be logged in to access this resource')
    @api.response(403, 'You are not authorized to access this resource')
    @api.response(404, 'Comparison not found')
    @api.response(500, 'Failed to delete comparison')
    @authentication_required
    def delete(self, current_user: User, comparison_id: int) -> typing.Any:
        """Delete comparison"""
        try:
            delete_comparison_by_id(comparison_id, current_user)
            return Response(status=204)
        except Forbidden as e:
            log.error('User %s is not authorized to delete comparison %s: %s', current_user, comparison_id, e)
            return Response("You are not authorized to delete this comparison", 403)
        except NotFound:
            log.error('Comparison %s not found', comparison_id)
            return Response("Comparison not found", 404)
        except Exception as e:
            log.exception('Failed to delete comparison %s: %s', comparison_id, e)
            return Response("Failed to delete comparison", 500)


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
