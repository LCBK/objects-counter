import logging

from natsort import natsorted
from sqlalchemy.exc import DatabaseError

from objects_counter.db.models import db, Image, ImageElement

log = logging.getLogger(__name__)


def insert_image(filepath: str, thumbnail_path: str) -> Image:
    image = Image(filepath=filepath, thumbnail=thumbnail_path)
    image.background_points = {"data": [{
        "position": [0, 0],
        "positive": False
    }]}
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


def get_images_by_ids(image_ids: list[int]) -> list[Image]:
    return Image.query.filter(Image.id.in_(image_ids)).all()


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


def bulk_set_elements(image: Image, elements: list[tuple[tuple[int, int], tuple[int, int]]]) -> None:
    delete_elements_by_image(image, do_commit=False)
    for element in elements:
        insert_element(image, element[0], element[1], do_commit=False)
    try:
        db.session.commit()
    except DatabaseError as e:
        log.exception('Failed to insert elements: %s', e)
        db.session.rollback()
        raise


def delete_elements_by_image(image: Image, do_commit: bool = True) -> None:
    for element in image.elements:
        db.session.delete(element)
    if do_commit:
        try:
            db.session.commit()
        except DatabaseError as e:
            log.exception('Failed to delete elements: %s', e)
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


def get_image_element_by_id(element_id: int) -> ImageElement:
    return ImageElement.query.get_or_404(element_id)


def get_background_points(image: Image) -> tuple[list[list[int]], list[bool]]:
    """
    :param image: Image object
    :return: Two lists, one with the positions of the points and one determining if the point on a given index
     is positive or negative
    """
    points = image.background_points["data"]
    response = ([], [])
    for point in points:
        response[0].append(point["position"])
        response[1].append(point["positive"])
    return response


def update_background_points(image_id: int, points: dict) -> None:
    Image.query.filter(Image.id == image_id).update({'background_points': points})
    try:
        db.session.commit()
    except DatabaseError as e:
        log.exception('Failed to update image: %s', e)
        db.session.rollback()
        raise


def update_element_classification(bounding_box: tuple[tuple[int, int], tuple[int, int]], classification: str,
                                  certainty: float) -> None:
    ImageElement.query.filter(ImageElement.top_left == bounding_box[0],
                              ImageElement.bottom_right == bounding_box[1]).update(
        {'classification': classification, 'certainty': certainty})
    try:
        db.session.commit()
    except DatabaseError as e:
        log.exception('Failed to update element: %s', e)
        db.session.rollback()
        raise


def update_element_classification_by_id(element_id: int, classification: str, certainty: float,
                                        do_commit: bool = True) -> None:
    ImageElement.query.filter_by(id=element_id).update({'classification': classification, 'certainty': certainty})
    if do_commit:
        try:
            db.session.commit()
        except DatabaseError as e:
            log.exception('Failed to update element: %s', e)
            db.session.rollback()
            raise


def bulk_update_element_classification_by_id(classifications: list[dict]) -> None:
    for classification in classifications:
        name = classification.get('name')
        if not name:
            raise ValueError('Classification name is required')
        elements = classification.get('elements', [])
        for element_id in elements:
            update_element_classification_by_id(element_id, name, 1., do_commit=False)
    try:
        db.session.commit()
    except DatabaseError as e:
        log.exception('Failed to update element classifications: %s', e)
        db.session.rollback()
        raise


def set_element_as_leader(element_id: int, image: Image, do_commit: bool = False) -> None:
    element_ids = [element.id for element in image.elements]
    if element_id not in element_ids:
        log.error('Element %s does not belong to image %s', element_id, image.id)
        raise ValueError(f'Element {element_id} does not belong to image {image.id}')
    ImageElement.query.filter_by(id=element_id).update({'is_leader': True})
    if do_commit:
        try:
            db.session.commit()
        except DatabaseError as e:
            log.exception('Failed to set element as leader: %s', e)
            db.session.rollback()
            raise


def serialize_image_as_result(image: Image) -> dict:
    classification_dict = {}

    for element in image.elements:
        element_data = element.as_dict()

        if element_data["classification"] is None:
            continue

        if element.certainty is not None:
            element_data["certainty"] = element.certainty
        else:
            element_data["certainty"] = 1

        if element.classification not in classification_dict:
            classification_dict[element.classification] = {
                "name": element.classification,
                "objects": []
            }

        classification_dict[element.classification]["objects"].append(element_data)

    # sort classifications by classification name
    classification_dict = dict(natsorted(classification_dict.items()))

    return {
        "count": len(image.elements),
        "classifications": list(classification_dict.values())
    }


def mark_leaders_in_image(image: Image, leader_ids: list[int]) -> None:
    for idx, leader in enumerate(leader_ids):
        set_element_as_leader(leader, image)
        ImageElement.query.filter_by(id=int(leader)).update({'classification': f'{idx + 1}'})
    try:
        db.session.commit()
    except DatabaseError as e:
        log.exception('Failed to mark leaders in image: %s', e)
        db.session.rollback()
        raise
