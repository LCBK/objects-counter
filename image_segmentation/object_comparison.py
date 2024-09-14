
import logging

from image_segmentation.segment_anything_object_counter import Image

log = logging.getLogger(__name__)

# TODO: store information about 2 images
# TODO: categories_1 & categories_2
# Check the number of element in image_1 and image_2
# If they match - all good
# If they do not mach - do the following
# For each category in category_1 get one image
# For each category in category_2 get one image
# Compare each image [1] with image [2] and find the one that is most similar
# After mapping each category compare the number of images in given category
# If category does not much it means that elements are missing

def compare_number_of_elements(image_1: Image, image_2: Image):
    pass

def find_missing_elements(image_1: Image, image_2: Image):
    pass

def map_categories():
    pass
