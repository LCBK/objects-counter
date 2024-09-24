# pylint: disable-all
# TODO: convert to documentation readme.md with below code as example

import cv2
import numpy as np

from image_segmentation.object_classification.classifier import ObjectClassifier
from image_segmentation.object_classification.feature_extraction import CosineSimilarity
from image_segmentation.object_detection.object_segmentation import ObjectSegmentation
from objects_counter.db.dataops.image import insert_image, get_image_by_id, update_background_points


def main():
    pass
    # # Add images
    # image_1 = ...
    # image_2
    #
    # # Path to SAM checkpoint
    # sam_checkpoint = ""
    #
    # # Initialize object segmentation using the SAM model
    # segmenter = ObjectSegmentation(sam_checkpoint)
    #
    # # Define points for mask calculation
    # points = [(300, 60), (600, 60), (400, 350), (400, 580), (350, 750)]
    # update_background_points(0, points)
    # update_background_points(1, points)
    #
    # # Calculate image mask based on provided points
    # mask_1 = segmenter.calculate_mask(image_1)
    # mask_2 = segmenter.calculate_mask(image_1)
    #
    # # Save the result mask as an image
    # result_mask_1 = np.array(mask_1) * 255
    # result_mask_2 = np.array(mask_2) * 255
    # cv2.imwrite("images/results/result_1.jpg", result_mask_1)
    # cv2.imwrite("images/results/result_2.jpg", result_mask_2)
    #
    # # Get the number of objects detected in the image
    # object_count_1 = segmenter.count_objects(image_1)
    # print(f"Number of objects detected: {object_count_1}")
    # object_count_2 = segmenter.count_objects(image_2)
    # print(f"Number of objects detected: {object_count_2}")
    #
    # # Initialize the CosineSimilarity model for object classification
    # similarity_model = CosineSimilarity()
    #
    # # Initialize object classifier and group objects by similarity
    # object_grouper = ObjectClassifier(segmenter, similarity_model)
    # object_grouper.group_objects_by_similarity(image_1)
    # object_grouper.group_objects_by_similarity(image_2)
    #
    # # Output the grouped objects' categories
    # print("Grouped objects:")
    #
    # # Iterate through the categories of objects and display details
    # for category_id, objects in enumerate(image_1.categories):
    #     # Extract indices of objects in the current category
    #     indices = [obj.index for obj in objects]
    #     # Detailed information about each object
    #     object_details = [(obj.index, obj.top_left_coord, obj.bottom_right_coord, obj.probability) for obj in objects]
    #
    #     print(f"Category {category_id}:")
    #     print(f"  Object indices: {indices}")
    #     print(f"  Object details: {object_details}")
    #
    # find_missing_elements(image_1, image_2, object_groupers)
    #


if __name__ == "__main__":
    main()
