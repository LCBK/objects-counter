import logging
import typing

from flask_restx import Resource, Namespace

from objects_counter.api.utils import authentication_optional

api = Namespace('default', description='Default namespace')
log = logging.getLogger(__name__)


@api.route('/is-alive')
class IsAlive(Resource):
    @api.response(200, "Flask is alive")
    @api.response(401, "User has invalid/outdated token")
    @authentication_optional  # if user has invalid/outdated token, it will return 401
    def get(self, _) -> typing.Any:
        return 'Flask is alive!', 200
