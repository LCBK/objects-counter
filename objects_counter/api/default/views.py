import typing

from flask_restx import Resource, Namespace

api = Namespace('default', description='Default namespace')


@api.route('/is-alive')
class IsAlive(Resource):
    def get(self) -> typing.Any:
        return 'Flask is alive!'


@api.route('/version')
class Version(Resource):
    def get(self) -> typing.Any:
        return '0.1'


@api.route('/submit')
class Submit(Resource):
    def post(self) -> typing.Any:
        return 'Not implemented', 501