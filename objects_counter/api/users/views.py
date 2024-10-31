import json
import logging
import typing

import jwt
from flask import request, Response, current_app
from flask_restx import Namespace, Resource

from objects_counter.api.utils import get_user_from_input
from objects_counter.api.users.models import user_model
from objects_counter.db.dataops.user import login, insert_user

api = Namespace('users', description='Users related operations')
log = logging.getLogger(__name__)
# pylint: disable=too-few-public-methods, broad-exception-caught


@api.route('/login')
class Login(Resource):
    @api.expect(user_model)
    def post(self) -> typing.Any:
        data = request.json
        try:
            username, password = get_user_from_input(data)
        except ValueError as e:
            log.exception('Failed to get user from input: %s', e)
            msg = e.args[1]
            return Response(msg, status=400)
        user = login(username, password)
        if user is None:
            return Response('Invalid username or password', status=404)
        try:
            token = jwt.encode({"user_id": user.id}, current_app.config['SECRET_KEY'], algorithm='HS256')
            return Response(json.dumps({
                'token': token,
                'user_id': user.id,
                'username': username
            }), status=200, content_type='application/json')
        except Exception as e:
            log.exception('Failed to generate token: %s', e)
            return Response("Failed to generate a token", status=500)


@api.route('/register')
class Register(Resource):
    @api.expect(user_model)
    def post(self) -> typing.Any:
        data = request.json
        try:
            username, password = get_user_from_input(data)
        except ValueError as e:
            log.exception('Failed to get user from input: %s', e)
            msg = e.args[0]
            return Response(msg, status=400)
        try:
            user = insert_user(username, password)
        except ValueError as e:
            log.exception('Failed to insert user: %s', e)
            msg = e.args[0]
            return Response(msg, status=400)
        return Response(json.dumps({
            'user_id': user.id,
            'username': user.username
        }), status=201)
