import logging

from sqlalchemy.exc import DatabaseError

from objects_counter.db.models import db, Image, ImageElement

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
    return Image.query.get_or_404(image_id)


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


def bulk_insert_elements(image: Image, elements: list[tuple[tuple[int, int], tuple[int, int]]]) -> None:
    for element in elements:
        insert_element(image, element[0], element[1], do_commit=False)
    try:
        db.session.commit()
    except DatabaseError as e:
        log.exception('Failed to insert elements: %s', e)
        db.session.rollback()
        raise


def insert_element(image: Image, top_left: tuple[int, int], bottom_right: tuple[int, int],
                   do_commit: bool = True) -> None:
    element = ImageElement(top_left=top_left, bottom_right=bottom_right)
    image.elements.append(element)
    if do_commit:
        try:
            db.session.commit()
        except DatabaseError as e:
            log.exception('Failed to insert element: %s', e)
            db.session.rollback()
            raise


def get_background_points(image: Image) -> list[list[int]]:
    return image.background_points["data"]


def update_background_points(image_id: int, points: dict) -> None:
    Image.query.filter(Image.id == image_id).update({'background_points': points})
    try:
        db.session.commit()
    except DatabaseError as e:
        log.exception('Failed to update image: %s', e)
        db.session.rollback()
        raise


def update_element_classification(bounding_box: tuple[tuple[int, int], tuple[int, int]],
                                  classification: str, certainty: float) -> None:
    ImageElement.query.filter(ImageElement.top_left == bounding_box[0], ImageElement.bottom_right == bounding_box[1]) \
        .update({'classification': classification, 'certainty': certainty})
    try:
        db.session.commit()
    except DatabaseError as e:
        log.exception('Failed to update element: %s', e)
        db.session.rollback()
        raise
