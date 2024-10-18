import logging

from sqlalchemy import and_
from sqlalchemy.exc import DatabaseError
from werkzeug.exceptions import Forbidden

from objects_counter.db.models import Result, db, User, ImageElement, Image

log = logging.getLogger(__name__)


def insert_result(user_id, image_id, response):
    result = Result(user_id=user_id, image_id=image_id, data=response)
    db.session.add(result)
    try:
        db.session.commit()
        return result
    except DatabaseError as e:
        log.exception('Failed to insert result: %s', e)
        db.session.rollback()
        raise


def get_results() -> list[Result]:
    return Result.query.all()


def get_user_results(user: User) -> list[Result]:
    return user.results


def get_user_results_serialized(user: User) -> list[dict]:
    results = get_user_results(user)
    results_list = []
    for result in results:
        results_list.append(result.as_dict())
    return results_list


def get_result_by_id(result_id: int) -> Result:
    return Result.query.filter_by(id=result_id).one_or_404()


def delete_result_by_id(result_id: int) -> None:
    result = Result.query.get(result_id)
    db.session.delete(result)
    try:
        db.session.commit()
    except DatabaseError as e:
        log.exception('Failed to delete result: %s', e)
        db.session.rollback()
        raise


def rename_classification(user: User, result_id: int, classification: str) -> None:
    result = get_result_by_id(result_id)
    if not user or result.user_id != user.id:
        log.error('User %s is not authorized to rename classification in result %s', user, result_id)
        raise Forbidden(f'User {user} is not authorized to rename classification in result {result_id}')
    count = ImageElement.query.join(Result, Result.image_id == ImageElement.image_id).filter(
        and_(
            ImageElement.classification == classification,
            Result.id == result_id
        )
    ).update(
        {ImageElement.classification: classification}
    )
    if count == 0:
        log.error('Classification %s not found in result %s', classification, result_id)
        raise ValueError(f'Classification {classification} not found in result {result_id}')
    try:
        db.session.commit()
        return count
    except DatabaseError as e:
        log.exception('Failed to rename classification: %s', e)
        db.session.rollback()
        raise
