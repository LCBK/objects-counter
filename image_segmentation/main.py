import os
import subprocess
import sys


def delete_files(*files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)


def main(original_image_path):
    removed_bg_image = "removed_bg.png"
    bw_image = "black_and_white.png"
    filled_holes_image = "filled_holes.png"

    # Step 1: Remove background
    subprocess.run([sys.executable, "image_segmentation\\helpers\\remove_background.py", original_image_path, removed_bg_image])

    # Step 2: Convert to black and white
    subprocess.run([sys.executable, "image_segmentation\\helpers\\black_and_white.py", "-i", removed_bg_image, "-o", bw_image])

    # Step 3: Fill holes
    subprocess.run([sys.executable, "image_segmentation\\helpers\\fill_holes.py", "-i", bw_image, "-o", filled_holes_image])

    # Step 4: Count objects
    subprocess.run([sys.executable, "image_segmentation\\helpers\\count_objects.py", "-i", filled_holes_image])

    # Clean up intermediate files
    # delete_files(removed_bg_image, bw_image, filled_holes_image)


if __name__ == "__main__":
    original_image_path = r'C:\Users\Alicja\PycharmProjects\objects-counter\image_segmentation\images\test2.jpg'
    main(original_image_path)
