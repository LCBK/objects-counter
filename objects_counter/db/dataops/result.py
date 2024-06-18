from sqlalchemy.exc import DatabaseError

from objects_counter.db.models import Result, db


def insert_result(user_id, image_id, response):
    result = Result(user_id=user_id, image_id=image_id, data=response['data'])
    db.session.add(result)
    try:
        db.session.commit()
    except DatabaseError as e:
        print('ERROR: failed to insert result', e)
        db.session.rollback()
        raise


def get_results() -> list[Result]:
    return Result.query.all()


def get_result_by_id(result_id: int) -> Result:
    return Result.query.get(result_id)


def delete_result_by_id(result_id: int) -> None:
    result = Result.query.get(result_id)
    db.session.delete(result)
    try:
        db.session.commit()
    except DatabaseError as e:
        print('ERROR: failed to delete result', e)
        db.session.rollback()
        raise
