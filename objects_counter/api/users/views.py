import json
import typing

import jwt
from flask import request, Response, current_app
from flask_restx import Namespace, Resource

from objects_counter.api.utils import get_user_from_input
from objects_counter.db.dataops.user import login, insert_user

api = Namespace('results', description='Results related operations')
# pylint: disable=too-few-public-methods, broad-exception-caught


@api.route('/login', doc=False)
class Login(Resource):
    def post(self) -> typing.Any:
        data = request.json
        try:
            username, password = get_user_from_input(data)
        except ValueError as e:
            return Response(str(e), status=400)
        user = login(username, password)
        if user is None:
            return Response('Invalid username or password', status=404)
        try:
            token = jwt.encode({"user_id": user.id}, current_app.config['SECRET_KEY'], algorithm='HS256')
            return Response(json.dumps({
                'token': token,
                'user_id': user.id
            }), status=200, content_type='application/json')
        except Exception as e:
            return Response(str(e), status=500)


@api.route('/register', doc=False)
class Register(Resource):
    def post(self) -> typing.Any:
        data = request.json
        try:
            username, password = get_user_from_input(data)
        except ValueError as e:
            return Response(str(e), status=400)
        try:
            user = insert_user(username, password)
        except ValueError as e:
            return Response(str(e), status=400)
        return Response(json.dumps({
            'user_id': user.id,
            'username': user.username
        }), status=201)
