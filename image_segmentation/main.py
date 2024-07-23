import cv2
from segment_anything_object_counter import SegmentAnythingObjectCounter
import numpy as np


image = cv2.imread("IMG_20240619_194828.jpg")
sam_checkpoint = "/home/shairys/objects/objects-counter/sam_vit_h_4b8939.pth"
sam = SegmentAnythingObjectCounter(sam_checkpoint)
index = sam.add_image(image, "ndarray")
points = [[1883.3709677419356, 1080.145161290323], [562.0806451612904, 873.693548387097],
          [2915.6290322580644, 1462.0806451612905]]
sam.calculate_image_mask(index=index, points=points)
result_mask = sam.get_image_mask(index=index)
result_mask = np.array(result_mask) * 255
cv2.imwrite("result.jpg", result_mask)
print(sam.get_object_count(index=index))



# import os
#
# from ultralytics import YOLO
#
# IMAGES_DIR = os.path.join('.', 'images')  # Directory containing input images
# OUTPUT_DIR = os.path.join('.', 'images', 'results')  # Directory to save annotated images
#
# # Ensure the output directory exists
# os.makedirs(OUTPUT_DIR, exist_ok=True)
#
# # Specify the path to the image file
# image_path = "images\\dice_image_1.jpg"
#
# # Load a model
# model_path = os.path.join('.', 'runs', 'detect', 'train4', 'weights', 'last.pt')
#
# model = YOLO("yolov8x-seg.pt")
# # Load the image using OpenCV
# #image = cv2.imread(image_path)
#
# # Perform inference on the image
# #results = model(["dice_image_1.jpg", "cat.jpg"])
# results = model(["test0.jpg"])
#
# # Draw bounding boxes and labels on the image
# #threshold = 0.5
# for result in results:
#     boxes = result.boxes  # Boxes object for bounding box outputs
#     print(boxes)
#     masks = result.masks  # Masks object for segmentation masks outputs
#     keypoints = result.keypoints  # Keypoints object for pose outputs
#     probs = result.probs  # Probs object for classification outputs
#     obb = result.obb  # Oriented boxes object for OBB outputs
#     result.show()  # display to screen
#     result.save(filename='result.jpg')  # save to disk