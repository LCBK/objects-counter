import logging

from sqlalchemy.exc import DatabaseError

from objects_counter.db.models import db, Image

log = logging.getLogger(__name__)


def insert_image(filepath: str) -> Image:
    image = Image(filepath=filepath)
    db.session.add(image)
    try:
        db.session.commit()
        return image
    except DatabaseError as e:
        log.exception('Failed to insert image: %s', e)
        db.session.rollback()
        raise


def get_images() -> list[Image]:
    return Image.query.all()


def get_image_by_id(image_id: int) -> Image:
    return Image.query.get(image_id)


def update_points(image_id: int, points: dict) -> Image:
    image = Image.query.get(image_id)
    image.background_points = points
    try:
        db.session.commit()
        return image
    except DatabaseError as e:
        log.exception('Failed to update image: %s', e)
        db.session.rollback()
        raise


def delete_image_by_id(image_id: int) -> None:
    image = Image.query.get(image_id)
    db.session.delete(image)
    try:
        db.session.commit()
    except DatabaseError as e:
        log.exception('Failed to delete image: %s', e)
        db.session.rollback()
        raise
