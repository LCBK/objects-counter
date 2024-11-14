import logging

from sqlalchemy.exc import DatabaseError
from werkzeug.exceptions import Forbidden

from objects_counter.db.dataops.image import get_image_by_id, serialize_image_as_result
from objects_counter.db.models import Result, db, User

log = logging.getLogger(__name__)


def insert_result(user_id, image_id, response):
    result = Result(user_id=user_id, data=response)
    image = get_image_by_id(image_id)
    image.result = result
    db.session.add(result)
    db.session.add(image)
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


def delete_result_by_id(result_id: int, user: User) -> None:
    result = Result.query.filter_by(id=result_id).one_or_404()
    if not user or result.user_id != user.id:
        log.error('User %s is not authorized to delete result %s', user, result_id)
        raise Forbidden(f'User {user} is not authorized to delete result {result_id}')
    db.session.delete(result)
    try:
        db.session.commit()
    except DatabaseError as e:
        log.exception('Failed to delete result: %s', e)
        db.session.rollback()
        raise


def rename_classification(user: User, result_id: int, old_classification: str, new_classification: str) -> int:
    if not new_classification:
        log.error('New classification is empty')
        raise ValueError('New classification is empty')
    result = get_result_by_id(result_id)
    count = 0
    if not user or result.user_id != user.id:
        log.error('User %s is not authorized to rename classification in result %s', user, result_id)
        raise Forbidden(f'User {user} is not authorized to rename classification in result {result_id}')
    for image in result.images:
        for element in image.elements:
            if element.classification == old_classification:
                element.classification = new_classification
                db.session.add(element)
                count += 1
    if count == 0:
        log.error('Classification %s not found in result %s', old_classification, result_id)
        raise ValueError(f'Classification {old_classification} not found in result {result_id}')
    try:
        result.data = serialize_image_as_result(result.images[0])
        db.session.add(result)
        db.session.commit()
        return count
    except DatabaseError as e:
        log.exception('Failed to rename classification: %s', e)
        db.session.rollback()
        raise
