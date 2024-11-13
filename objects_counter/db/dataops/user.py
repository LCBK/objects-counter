import logging

from sqlalchemy.exc import DatabaseError
from werkzeug.exceptions import NotFound

from objects_counter.db.models import User, db, bcrypt

log = logging.getLogger(__name__)


def get_users() -> list[User]:
    return User.query.all()


def get_user_by_id(user_id: int) -> User:
    return User.query.get(user_id)


def get_user_by_username(username: str) -> User:
    return User.query.filter_by(username=username).one_or_none()


def insert_user(username: str, password: str) -> User:
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        get_user_by_username(username)
        raise ValueError('Username already exists')
    except NotFound:
        pass
    user = User(username=username, password=password_hash)
    db.session.add(user)
    try:
        db.session.commit()
        return user
    except DatabaseError as e:
        log.exception('Failed to insert user: %s', e)
        db.session.rollback()
        raise


def login(username: str, password: str) -> User | None:
    user = get_user_by_username(username)
    if user is None or not bcrypt.check_password_hash(user.password, password):
        return None
    return user


def delete_user_by_id(user_id: int) -> None:
    user = User.query.get(user_id)
    db.session.delete(user)
    try:
        db.session.commit()
    except DatabaseError as e:
        log.exception('Failed to delete user: %s', e)
        db.session.rollback()
        raise


def update_user_password(user_id: int, password: str) -> None:
    user = User.query.get(user_id)
    user.password = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        db.session.commit()
    except DatabaseError as e:
        log.exception('Failed to update user password: %s', e)
        db.session.rollback()
        raise
