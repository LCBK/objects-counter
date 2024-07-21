from flask_restx import fields

from objects_counter.api import api

user = api.model('User', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password'),
})
