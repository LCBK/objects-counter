import typing

from flask_restx import Namespace, Resource
from werkzeug.exceptions import NotFound

from objects_counter.db.dataops.result import get_result_by_id, get_results

api = Namespace('results', description='Results related operations')
# pylint: disable=too-few-public-methods, broad-exception-caught


@api.route('/')
class GetResults(Resource):
    def get(self) -> typing.Any:
        return get_results(), 200


@api.route('/<int:result_id>')
class GetResult(Resource):
    @api.doc(params={'result_id': 'The result ID'})
    def get(self, result_id: int) -> typing.Any:
        if result_id < 0:
            return 'Invalid result ID', 400
        try:
            result = get_result_by_id(result_id)
            return result, 200
        except NotFound as e:
            return str(e), 404
        except Exception as e:
            return str(e), 500
