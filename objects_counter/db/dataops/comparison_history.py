import logging

from natsort import natsorted
from sqlalchemy.exc import DatabaseError

from objects_counter.db.models import Comparison, db, User, Dataset, Image

log = logging.getLogger(__name__)


def insert_comparison(user: User, dataset: Dataset, images: list[Image], diff: dict) -> Comparison:
    comparison = Comparison(user_id=user.id, dataset_id=dataset.id, diff=dict(natsorted(diff.items())))
    for image in images:
        image.comparison = comparison
    db.session.add_all([comparison] + images)
    try:
        db.session.commit()
        return comparison
    except DatabaseError as e:
        log.exception('Failed to insert comparison: %s', e)
        db.session.rollback()
        raise


def get_comparisons_by_user_id(user_id: User) -> list[dict]:
    comparisons = Comparison.query.filter_by(user_id=user_id).all()
    return [comparison.as_dict() for comparison in comparisons]
