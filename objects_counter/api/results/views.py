import typing
from time import sleep

from flask_restx import Namespace, Resource

api = Namespace('results', description='Results related operations')


@api.route('/get')
class GetResults(Resource):
    def get(self) -> typing.Any:
        return 'Not implemented', 501


@api.route('/<int:result_id>')
class GetResult(Resource):
    @api.doc(params={'result_id': 'The result ID'})
    def get(self, result_id: int) -> typing.Any:
        sleep(5)
        print(result_id)
        return 'Not implemented', 501


@api.route('/<int:result_id>/rate')
class RateResult(Resource):
    @api.doc(params={'result_id': 'The result ID'})
    def patch(self, result_id: int) -> typing.Any:
        print(result_id)
        return 'Not implemented', 501
