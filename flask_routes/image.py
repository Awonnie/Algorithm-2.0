
import cv2
import supervision as sv
from flask import Blueprint, jsonify, request
from inference import get_roboflow_model

import random
import os

from .helper import clear_images, setup_img_folders

# Local Imports
from consts import CV_API_KEY, MODEL_ID

image = Blueprint('image', __name__)

# Initialise model
robomodel = get_roboflow_model(model_id= MODEL_ID, api_key=CV_API_KEY) 

@image.route('/image', methods=['POST'])
def image_predict():
    """
    This is the main endpoint for the image prediction algorithm

    filename format: "<timestamp>_<obstacle_id>_<signal>.jpeg
    
    :return: a json object with a key "result" and value a dictionary with keys "obstacle_id" and "image_id"
    """
    print(f"Request: {request.files}")
    file = request.files['file']
    filename = file.filename

    # Initialise folders
    setup_img_folders()
    clear_images()

    raw_img_path = 'images/raw'
    annotated_img_path = 'images/annotated'

    # Save the raw images to raw_img_path
    file.save(os.path.join(raw_img_path, filename))
    constituents = file.filename.split("_")
    obstacle_id = constituents[1]

    frame = cv2.imread(os.path.join(raw_img_path, filename))  

    if frame is None:
        print("Failed to load image")
        result = {
            "obstacle_id": 1,
            "image_id": 23
        }
        return jsonify(result)

    results = robomodel.infer(image = frame,
                                confidence = 0.5,
                                iou_threshold=0.5)
    detections = sv.Detections.from_inference(results[0].dict(by_alias=True, exclude_none=True))

    class_name = detections.data['class_name'][0]
    image_id = int(class_name[2:])

    # Annotate the frame
    bounding_box_annotator = sv.BoundingBoxAnnotator()
    label_annotator = sv.LabelAnnotator()

    # Create supervision annotators
    annotated_frame = bounding_box_annotator.annotate(scene=frame, detections=detections)
    annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections)

    # Generate a unique filename for the annotated image
    rand = random.randint(1000, 9999)
    annotated_filename = f"{annotated_img_path}/annotated_image_{class_name}_{rand}.jpg"
    
    # Save the annotated image
    cv2.imwrite(annotated_filename, annotated_frame)

    # Return the obstacle_id and image_id
    result = {
        "obstacle_id": obstacle_id,
        "image_id": image_id
    }
    return jsonify(result)