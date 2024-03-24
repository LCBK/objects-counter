from flask_restx import Resource

from small_objects_counter.api import api


@api.route('/is-alive')
def is_alive():
    return 'Flask is alive!'


@api.route('/version')
def version():
    return '0.1'


@api.route('/submit')
class Submit(Resource):
    @api.response(200, 'Success')
    @api.expect()
    def post(self):
        try:
            process(iamge)
            return 'content', 200
        except ValueError as e:
            return str(e), 400
        except Exception as e:
            return str(e), 500


