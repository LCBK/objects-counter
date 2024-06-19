from functools import wraps
from http import HTTPStatus

import jwt
from flask import request, Response, current_app

from objects_counter.db.dataops.user import get_user_by_id


def authentication_required(f):
    @wraps(f)
    def decorated_function(self, *args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if not token:
            return Response('Authentication required', HTTPStatus.UNAUTHORIZED)
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = get_user_by_id(data['user_id'])
            if current_user is None:
                return Response('Invalid token', HTTPStatus.UNAUTHORIZED)
        except jwt.ExpiredSignatureError:
            return Response('Token expired', HTTPStatus.UNAUTHORIZED)
        except Exception as e:  # pylint: disable=broad-except
            return Response({
                'message': 'Issue while processing authentication',
                'error': str(e)
            }, HTTPStatus.INTERNAL_SERVER_ERROR)

        return f(self, current_user, *args, **kwargs)

    return decorated_function


def authentication_optional(f):
    @wraps(f)
    def decorated_function(self, *args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
        if token:
            try:
                data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
                current_user = get_user_by_id(data['user_id'])
                if current_user is None:
                    return Response('Invalid token', HTTPStatus.UNAUTHORIZED)
            except Exception as e:  # pylint: disable=broad-except
                return Response({
                    'message': 'Issue while processing authentication',
                    'error': str(e)
                }, HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            current_user = None

        return f(self, current_user, *args, **kwargs)

    return decorated_function


def validate_password(password: str) -> bool:
    return (len(password) >= 8 and any(char.isdigit() for char in password) and any(char.isupper() for char in password)
            and any(char.islower() for char in password) and any(char in '!@#$%^&*()-+' for char in password))


def get_user_from_input(data):
    if not data:
        raise ValueError('No input data provided')
    username = data.get('username')
    password = data.get('password')
    if not username.isalnum() or not validate_password(password):
        raise ValueError('Invalid input data')
    return username, password
