import json
from sortedcontainers import SortedDict
import cv2
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import os

def generate_colors(num_classes):
    """
    Generate distinct colors for each class using a colormap.

    Args:
        num_classes (int): Number of distinct classes.

    Returns:
        dict: A dictionary mapping class indices to colors.
    """
    # Use the 'hsv' colormap from matplotlib, which gives a good spread of colors
    colormap = plt.get_cmap('hsv')
    
    # Generate an array of color indices
    color_indices = np.linspace(0, 1, num_classes)
    
    # Create a dictionary mapping class index to color
    class_colors = {i: colormap(color_indices[i])[:3] for i in range(num_classes)}
    
    # Convert colors from RGB in [0,1] to BGR in [0,255]
    class_colors_bgr = {i: tuple(int(255 * c) for c in reversed(class_colors[i])) for i in range(num_classes)}
    
    return class_colors_bgr

# Example usage
num_noun_classes = 310
noun_class_colors = generate_colors(num_noun_classes)

def extract_frame_id(frame_annotation_metadata):
    """
    Extracts the frame_id from the given frame annotation metadata.

    Args:
        frame_annotation_metadata (dict): A dictionary containing the image annotation, 
                                 which includes 'image_path' and 'name' keys.

    Returns:
        int: The extracted frame_id as an integer.
    """
    # Extract the image name from the annotation
    image_name = frame_annotation_metadata['name']
    
    # Assuming the frame_id is the numeric part after the last underscore in the image name
    frame_id_str = image_name.split('_')[-1].replace('.jpg', '')
    
    # Convert the frame_id to an integer
    frame_id = int(frame_id_str)
    
    return frame_id

def has_visor(video_id):
    return os.path.exists(annotation_path(video_id))

def annotation_path(video_id):
    return f"/home/ec2-user/environment/data/visor-annotations/{video_id}.json"

def load_annotations(video_id):
    """
    Loads annotations from a JSON file based on `video_id` and organizes them in a SortedDict by frame_id.

    Args:
        video_id (str): Video ID

    Returns:
        SortedDict: A SortedDict where keys are frame_ids and values are lists of annotations for that frame.
    """
    with open(annotation_path(video_id), 'r') as f:
        data = json.load(f)

    annotations_by_frame = SortedDict()

    for frame in data['video_annotations']:
        
        frame_id = extract_frame_id(frame['image'])
        # frame_id = int(frame['image']['frame_id'])  # Assuming the JSON contains a 'frame_id' key
        annotations_by_frame[frame_id] = frame

    return annotations_by_frame

def find_nearest_annotations(frame_id, annotations_by_frame):
    """
    Finds the nearest annotations for a given frame_id using a SortedDict.

    Args:
        frame_id (int): The frame ID for which to retrieve annotations.
        annotations_by_frame (SortedDict): SortedDict of annotations organized by frame_id.

    Returns:
        list: The nearest annotations for the given frame_id.
    """
    # If the exact frame_id exists in the dictionary, return its annotations
    if frame_id in annotations_by_frame:
        return annotations_by_frame[frame_id]

    # Find the position where frame_id would be inserted to keep the keys sorted
    pos = annotations_by_frame.bisect_left(frame_id)

    if pos == 0:
        # No smaller frame_id, return the annotations for the first frame_id
        nearest_frame_id = annotations_by_frame.keys()[0]
    elif pos == len(annotations_by_frame):
        # No larger frame_id, return the annotations for the last frame_id
        nearest_frame_id = annotations_by_frame.keys()[-1]
    else:
        # Nearest frame_id is either just before or just after the given frame_id
        prev_frame_id = annotations_by_frame.keys()[pos - 1]
        next_frame_id = annotations_by_frame.keys()[pos]
        # Choose the closer frame_id between prev_frame_id and next_frame_id
        nearest_frame_id = prev_frame_id if (frame_id - prev_frame_id) <= (next_frame_id - frame_id) else next_frame_id

    return annotations_by_frame[nearest_frame_id]


def scale_mask_coords(mask_coords, expected_shape, actual_shape):
    """
    Scales mask coordinates from an image with actual_shape to expected_shape.

    Args:
        mask_coords: List of coordinates representing the mask polygon.
        expected_shape: Expected shape of the image (height, width).
        actual_shape: Actual shape of the image (height, width).

    Returns:
        Scaled mask coordinates as a NumPy array.
    """
    height_scale = actual_shape[0] / expected_shape[0]
    width_scale = actual_shape[1] / expected_shape[1]
    scaled_coords = np.array([[int(x * width_scale), int(y * height_scale)] for x, y in mask_coords])
    return scaled_coords

def calculate_bounding_rectangle(coordinates):
    """
    Calculates the bounding rectangle that encompasses a set of coordinates.

    Args:
        coordinates: A list of lists representing [x, y] coordinates.

    Returns:
        A list of lists representing the four corner points of the bounding rectangle:
        [[x_min, y_min], [x_max, y_min], [x_max, y_max], [x_min, y_max]].
    """
    points = np.array(coordinates, dtype=np.int32)
    rect = cv2.minAreaRect(points)
    box = cv2.boxPoints(rect)
    box = np.intp(box)
    return box.tolist()

def apply_occlusion(img, annotations, noun_class_colors, expected_shape=(1080, 1920, 3)):
    """
    Applies occlusion to the image based on given annotations with distinct colors for each noun class.

    Args:
        img: Original image.
        annotations: Annotations to use for occlusion.
        noun_class_colors: Dictionary mapping noun classes to colors.
        expected_shape: Expected shape of the image (height, width, channels).
    
    Returns:
        The occluded image.
    """
    if img.shape != expected_shape:
        actual_shape = img.shape[:2]

    mask = img.copy()

    for annotation in annotations['annotations']:
        noun_class = annotation['class_id']

        # mask_color = noun_class_colors[noun_class]
        mask_color = (0, 0, 0)
        segments = annotation['segments']
        
        if img.shape != expected_shape:
            segments = [scale_mask_coords(segment, expected_shape[:2], actual_shape) for segment in segments]

        for segment in segments:
            mask_coords = calculate_bounding_rectangle(segment)
            mask = cv2.fillPoly(mask, [np.array(mask_coords, dtype=np.int32)], mask_color)

    return mask

def overlay_mask(image, segments, mask_color=(0, 0, 255), expected_shape=(1080, 1920, 3)):
    """
    Overlays a mask from the specified segments onto the given image.

    Args:
        image: Original image.
        segments: List of mask segments to apply.
        mask_color: Color of the mask (BGR format).
        expected_shape: Expected shape of the image (height, width, channels).
    
    Returns:
        The masked image.
    """
    if image.shape != expected_shape:
        actual_shape = image.shape[:2]

    mask = image.copy()

    for mask_coords in segments:
        if image.shape != expected_shape:
            mask_coords = scale_mask_coords(mask_coords, expected_shape[:2], actual_shape)

        mask_coords = calculate_bounding_rectangle(mask_coords)
        mask = cv2.fillPoly(mask, [np.array(mask_coords, dtype=np.int32)], mask_color)

    return mask

# annotations_by_frame = load_annotations('../P01_01.json')
# print(find_nearest_annotations(93349, annotations_by_frame))