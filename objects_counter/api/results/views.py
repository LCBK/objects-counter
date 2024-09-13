import logging
import typing

from flask import Response, jsonify
from flask_restx import Namespace, Resource
from werkzeug.exceptions import NotFound

from objects_counter.api.utils import authentication_required
from objects_counter.db.dataops.result import get_result_by_id, get_user_results_serialized
from objects_counter.db.models import User

api = Namespace('results', description='Results related operations')
log = logging.getLogger(__name__)
# pylint: disable=too-few-public-methods, broad-exception-caught


@api.route('/')
class GetResults(Resource):
    @authentication_required
    def get(self, current_user: User) -> typing.Any:
        return jsonify(get_user_results_serialized(current_user))


@api.route('/<int:result_id>')
class GetResult(Resource):
    @api.doc(params={'result_id': 'The result ID'})
    @authentication_required
    def get(self, current_user: User, result_id: int) -> typing.Any:
        result_id = int(result_id)
        if result_id < 0:
            return Response('Invalid result ID', 400)
        try:
            result = get_result_by_id(result_id)
            if result.user_id != current_user.id:
                return Response('Unauthorized', 403)
            return Response(result, 200)
        except NotFound as e:
            log.exception("Result %s not found: %s", result_id, e)
            return Response(f"Result {result_id} not found", 404)
        except Exception as e:
            log.exception("Failed to get result %s: %s", result_id, e)
            return Response("Failed to get requested result", 500)
