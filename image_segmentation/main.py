# pylint: disable-all
# TODO: convert to documentation readme.md with below code as example
import cv2
from segment_anything_object_counter import SegmentAnythingObjectCounter
import numpy as np


image = cv2.imread("images/test2.jpg")
sam_checkpoint = "C:\\Users\\kobryl\\inz\\instance\\sam_vit_h_4b8939.pth"
sam = SegmentAnythingObjectCounter(sam_checkpoint)
index = sam.add_image(image)
points = [[1883.3709677419356, 1080.145161290323], [562.0806451612904, 873.693548387097],
          [2915.6290322580644, 1462.0806451612905]]
sam.calculate_image_mask(index=index, points=points)
result_mask = sam.get_image_mask(index=index)
result_mask = np.array(result_mask) * 255
print(result_mask)
print(max(result_mask.flatten()))
cv2.imwrite("result.jpg", result_mask)
print(sam.get_object_count(index=index))
