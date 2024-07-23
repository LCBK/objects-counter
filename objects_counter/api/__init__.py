from flask import Blueprint
from flask_restx import Api

from objects_counter.api.default.views import api as default
from objects_counter.api.results.views import api as results
from objects_counter.api.users.views import api as users


class FixedApi(Api):
    def ns_urls(self, ns, urls):
        def fix(url):
            return url[1:] if url.startswith('//') else url

        return [fix(url) for url in super().ns_urls(ns, urls)]


blueprint = Blueprint('api', __name__, url_prefix='/api')
api = FixedApi(blueprint)
api.add_namespace(default, '/')
api.add_namespace(results, '/results')
api.add_namespace(users, '/users')
