import logging

from sqlalchemy.exc import DatabaseError
from werkzeug.exceptions import Forbidden

from objects_counter.db.dataops.image import get_image_by_id, update_element_classification_by_id, set_element_as_leader
from objects_counter.db.models import User, Dataset, db

log = logging.getLogger(__name__)


def insert_dataset(user_id: int, image_id: int, name: str, classifications: list[dict]) -> Dataset:
    dataset = Dataset(user_id=user_id, name=name)
    image = get_image_by_id(image_id)
    image.dataset = dataset
    for classification in classifications:
        elements = classification.get('elements', [])
        class_name = classification.get('name')
        leader_id = int(classification.get('leader'))
        if not elements or not class_name or not leader_id:
            log.error('Classification %s is missing required fields: %s %s', classification, class_name, elements)
            raise ValueError(f'Classification {classification} is missing required fields')
        for element in elements:
            update_element_classification_by_id(int(element), class_name, 1., do_commit=False)
        set_element_as_leader(leader_id, image)
    db.session.add(image)
    db.session.add(dataset)
    try:
        db.session.commit()
        return dataset
    except DatabaseError as e:
        log.exception('Failed to insert dataset: %s', e)
        db.session.rollback()
        raise


def add_image_to_dataset(dataset_id: int, image_id: int) -> Dataset:
    dataset = get_dataset_by_id(dataset_id)
    image = get_image_by_id(image_id)
    if image.user_id != dataset.user_id:
        log.error('Image %s does not belong to dataset %s owner', image_id, dataset_id)
        raise Forbidden(f'Image {image_id} does not belong to dataset {dataset_id}')
    image.dataset = dataset
    db.session.add(image)
    try:
        db.session.commit()
        return dataset
    except DatabaseError as e:
        log.exception('Failed to add image to dataset: %s', e)
        db.session.rollback()
        raise


def get_user_datasets(user: User) -> list[Dataset]:
    return user.datasets


def get_user_datasets_serialized(user: User) -> list[dict]:
    datasets = get_user_datasets(user)
    serialized_datasets = []
    for dataset in datasets:
        serialized_datasets.append(dataset.as_dict())
    return serialized_datasets


def get_dataset_by_id(dataset_id: int) -> Dataset:
    return Dataset.query.filter_by(id=dataset_id).one_or_404()


def rename_dataset(dataset_id: int, new_name: str, user: User) -> Dataset:
    dataset = get_dataset_by_id(dataset_id)
    if dataset.user_id != user.id:
        log.error('User %s is not authorized to rename dataset %s', user, dataset_id)
        raise Forbidden(f'User {user} is not authorized to rename dataset {dataset_id}')
    if not new_name:
        log.error('New name is empty')
        raise ValueError('New name is empty')
    dataset.name = new_name
    try:
        db.session.commit()
        return dataset
    except DatabaseError as e:
        log.exception('Failed to rename dataset: %s', e)
        db.session.rollback()
        raise


def delete_dataset_by_id(dataset_id: int, user: User) -> None:
    dataset = get_dataset_by_id(dataset_id)
    if dataset.user_id != user.id:
        log.error('User %s is not authorized to delete dataset %s', user, dataset_id)
        raise Forbidden(f'User {user} is not authorized to delete dataset {dataset_id}')
    db.session.delete(dataset)
    try:
        db.session.commit()
    except DatabaseError as e:
        log.exception('Failed to delete dataset: %s', e)
        db.session.rollback()
        raise
