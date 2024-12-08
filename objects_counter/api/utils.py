import base64
import gzip
import io
import logging
from functools import wraps
from http import HTTPStatus

import jwt
from flask import request, Response, current_app
from jwt import DecodeError

from objects_counter.consts import MAX_DB_STRING_LENGTH, MIN_USERNAME_LENGTH
from objects_counter.db.dataops.user import get_user_by_id
from objects_counter.db.models import Dataset, Result, Comparison

log = logging.getLogger(__name__)


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
                log.error('Invalid token')
                return Response('Invalid token', HTTPStatus.UNAUTHORIZED)
        except (jwt.ExpiredSignatureError, DecodeError) as e:
            log.error('Issue while processing authentication: %s', e)
            return Response('Invalid token', HTTPStatus.UNAUTHORIZED)
        except Exception as e:  # pylint: disable=broad-except
            log.exception('Issue while processing authentication: %s', e)
            return Response({
                'message': 'Issue while processing authentication'
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
                    log.error('Invalid token')
                    return Response('Invalid token', HTTPStatus.UNAUTHORIZED)
            except (jwt.ExpiredSignatureError, DecodeError) as e:
                log.exception('Error while processing authentication: %s', e)
                return Response('Invalid token', HTTPStatus.UNAUTHORIZED)
            except Exception as e:  # pylint: disable=broad-except
                log.exception('Issue while processing authentication: %s', e)
                return Response({
                    'message': 'Issue while processing authentication'
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
    if len(username) < MIN_USERNAME_LENGTH:
        raise ValueError(f'Username too short (min. {MIN_USERNAME_LENGTH})')
    if len(username) > MAX_DB_STRING_LENGTH:
        raise ValueError(f'Username too long (max. {MAX_DB_STRING_LENGTH})')
    password = data.get('password')
    if not username.isalnum() or not validate_password(password):
        raise ValueError('Invalid input data')
    return username, password


def gzip_compress(data: bytes) -> bytes:
    buffer = io.BytesIO()
    with gzip.GzipFile(fileobj=buffer, mode='wb') as f:
        f.write(data)
    return buffer.getvalue()


def get_thumbnails(collection: list[Dataset | Result | Comparison]) -> list[dict]:
    thumbnails = []
    for item in collection:
        if len(item.images) == 0:
            continue

        with open(item.images[0].thumbnail, 'rb') as thumbnail:
            base64_thumbnail = base64.b64encode(thumbnail.read())

        thumbnails.append({
            'id': item.id,
            'thumbnail': base64_thumbnail.decode('utf-8')
        })
    return thumbnails
