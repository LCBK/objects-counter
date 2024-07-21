import typing

from flask import Response, jsonify
from flask_restx import Namespace, Resource
from werkzeug.exceptions import NotFound

from objects_counter.api.utils import authentication_required
from objects_counter.db.dataops.result import get_result_by_id, get_user_results_serialized
from objects_counter.db.models import User

api = Namespace('results', description='Results related operations')
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
        if result_id < 0:
            return Response('Invalid result ID', 400)
        try:
            result = get_result_by_id(result_id)
            if result.user_id != current_user.id:
                return Response('Unauthorized', 403)
            return Response(result, 200)
        except NotFound as e:
            return Response(str(e), 404)
        except Exception as e:
            return Response(str(e), 500)
