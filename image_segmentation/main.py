# pylint: disable-all
# TODO: convert to documentation readme.md with below code as example

import cv2
import numpy as np

from image_segmentation.object_classification import CosineSimilarity, ObjectClassifier
from image_segmentation.segment_anything_object_counter import SegmentAnythingObjectCounter


def main():
    image = cv2.imread("images/img_1.png")

    sam_checkpoint = "C:/Users/Alicja/Desktop/Studia/Projekt inżynierski/sam_vit_h_4b8939.pth"
    segmenter = SegmentAnythingObjectCounter(sam_checkpoint)

    image_index = segmenter.add_image(image)
    points = [[300, 60], [600, 60], [400, 350], [400, 580], [350, 750]]
    segmenter.calculate_image_mask(image_index, points=points)

    result_mask = segmenter.get_image_mask(image_index)
    result_mask = np.array(result_mask) * 255
    cv2.imwrite("images/results/result.jpg", result_mask)

    object_count = segmenter.get_object_count(image_index)
    print(f"Number of objects detected: {object_count}")

    similarity_model = CosineSimilarity()

    object_grouper = ObjectClassifier(segmenter, similarity_model)

    object_grouper.group_objects_by_similarity()
    print("Grouped objects:")

    # Iterate through the categories of objects
    for category_id, objects in enumerate(segmenter.images[0].categories):
        # Extract indices of objects in the current category
        indices = [obj.index for obj in objects]
        # Detailed information about each object
        object_details = [(obj.index, obj.top_left_coord, obj.bottom_right_coord, obj.probability) for obj in objects]
        print(f"Category {category_id}:")
        print(f"  Object indices: {indices}")
        print(f"  Object details: {object_details}")


if __name__ == "__main__":
    main()
