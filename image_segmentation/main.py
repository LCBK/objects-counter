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
    points = [[462, 59], [538, 364], [237, 503], [588, 740]]
    segmenter.calculate_image_mask(index=image_index, points=points)

    result_mask = segmenter.get_image_mask(index=image_index)
    result_mask = np.array(result_mask) * 255
    cv2.imwrite("images/results/result.jpg", result_mask)

    object_count = segmenter.get_object_count(index=image_index)
    print(f"Number of objects detected: {object_count}")

    similarity_model = CosineSimilarity()

    object_grouper = ObjectClassifier(segmenter, similarity_model)

    grouped_objects = object_grouper.group_objects_by_similarity(threshold=0.7)
    print("Grouped objects:")

    for category_id, objects in grouped_objects.items():
        indices = [obj[0] for obj in objects]
        print(f"Category {category_id}: Objects {indices}")


if __name__ == "__main__":
    main()
