from sqlalchemy.exc import DatabaseError

from objects_counter.db.models import db, Image


def insert_image(filepath: str) -> Image:
    image = Image(filepath=filepath)
    db.session.add(image)
    try:
        db.session.commit()
        return image
    except DatabaseError as e:
        print('ERROR: failed to insert image', e)
        db.session.rollback()
        raise


def get_images() -> list[Image]:
    return Image.query.all()


def get_image_by_id(image_id: int) -> Image:
    return Image.query.get(image_id)


def delete_image_by_id(image_id: int) -> None:
    image = Image.query.get(image_id)
    db.session.delete(image)
    try:
        db.session.commit()
    except DatabaseError as e:
        print('ERROR: failed to delete image', e)
        db.session.rollback()
        raise
