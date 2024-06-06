import typing
from time import sleep

from flask_restx import Namespace, Resource

api = Namespace('results', description='Results related operations')


@api.route('/get')
class GetResults(Resource):
    def get(self) -> typing.Any:
        return 'Not implemented', 501


@api.route('/<int:id>')
class GetResult(Resource):
    @api.doc(params={'id': 'The result ID'})
    def get(self, id: int) -> typing.Any:
        sleep(5)
        return 'Not implemented', 501


@api.route('/<int:id>/rate')
class RateResult(Resource):
    @api.doc(params={'id': 'The result ID'})
    def patch(self, id: int) -> typing.Any:
        return 'Not implemented', 501
