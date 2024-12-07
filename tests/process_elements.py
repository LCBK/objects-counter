from pathlib import Path

import cv2
import numpy as np

from image_segmentation.object_detection.object_segmentation import ObjectSegmentation
from objects_counter.db.models import Image


def mouse_callback(event, x, y, flags, param):
    background_points, display_image_original, window_name = param

    if event == cv2.EVENT_LBUTTONDBLCLK:
        background_points.append({"position": [x, y], "positive": True})
    elif event == cv2.EVENT_RBUTTONDBLCLK:
        background_points.append({"position": [x, y], "positive": False})

    update_display(window_name, display_image_original, background_points)


def update_display(window_name, base_image, points):
    image_with_points = base_image.copy()
    for point in points:
        color = (0, 0, 255) if point["positive"] else (255, 0, 0)
        cv2.circle(image_with_points, tuple(point["position"]), radius=5, color=color, thickness=-1)
    cv2.imshow(window_name, image_with_points)


def scale_image(image, scale_percent):
    height, width = image.shape[:2]
    new_width = int(width * scale_percent / 100)
    new_height = int(height * scale_percent / 100)
    return cv2.resize(image, (new_width, new_height))


def center_window(window_name, width, height):
    """
    Centers the OpenCV window on the screen.
    """
    screen_width = 1920
    screen_height = 1080
    x_pos = (screen_width - width) // 4
    y_pos = (screen_height - height) // 4
    cv2.moveWindow(window_name, x_pos, y_pos)


def process_images(folder_path, checkpoint_path):
    segmentation = ObjectSegmentation(checkpoint_path)
    window_name = "Image Segmentation"
    cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

    output_folder = Path("elements")
    output_folder.mkdir(exist_ok=True)

    for idx, image_file in enumerate(Path(folder_path).glob("*.jpg")):
        file_name = image_file.stem
        try:
            game_name, element_type, illumination_type, element_color = file_name.split('-')
        except ValueError:
            print(f"Skipping file with unexpected name format: {file_name}")
            continue

        print(f"Processing image: {image_file}")

        image_data = cv2.imread(str(image_file))
        if image_data is None:
            print(f"Failed to load image: {image_file}")
            continue

        image = Image(filepath=str(image_file), id=idx)
        background_points = []

        display_image = scale_image(image_data, scale_percent=15)
        height, width = display_image.shape[:2]
        center_window(window_name, width, height)

        cv2.setMouseCallback(window_name, mouse_callback, [background_points, display_image, window_name])

        while True:
            update_display(window_name, display_image, background_points)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("r"):
                print("Resetting points.")
                background_points.clear()
            elif key == ord("m"):
                if not background_points:
                    print("No points selected. Please add points first.")
                    continue

                print("Calculating mask...")
                image.background_points = {"data": background_points}
                mask = segmentation.calculate_mask(image)

                if mask is None:
                    print("Mask calculation failed.")
                    continue

                mask_preview = cv2.bitwise_and(image_data, image_data, mask=np.invert(mask).astype("uint8"))
                mask_preview = scale_image(mask_preview, scale_percent=15)
                update_display(window_name, mask_preview, [])

                print("Press 'y' to accept mask or any other key to adjust.")
                preview_key = cv2.waitKey(0)
                if preview_key == ord("y"):
                    print("Mask accepted.")
                    break
            elif key == ord("q"):
                print("Proceeding to next image.")
                break

        bounding_boxes = segmentation.get_bounding_boxes(image, mask)
        if not bounding_boxes:
            print(f"No objects found in: {image_file}")
            continue

        no_background_image = segmentation.get_image_without_background(image, mask)
        for obj_idx, (start, end) in enumerate(bounding_boxes):
            x1, y1 = start
            x2, y2 = end
            object_image = no_background_image.crop((x1, y1, x2, y2))
            output_name = f"{game_name}-{illumination_type}-{element_type}-{element_color}-{obj_idx}.jpg"
            output_path = output_folder / output_name
            object_image.save(str(output_path))
            print(f"Saved object as: {output_path}")

    cv2.destroyAllWindows()


if __name__ == "__main__":
    input_folder = ""
    checkpoint = ""

    try:
        process_images(input_folder, checkpoint)
    except Exception as e:
        print(f"An error occurred: {e}")
