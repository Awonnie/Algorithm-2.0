
import cv2
import supervision as sv
from flask import Blueprint, jsonify, request
from inference import get_roboflow_model

import random
import os


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
    file = request.files['file']
    filename = file.filename
    raw_img_path = 'images/raw'
    annotated_img_path = 'images/annotated'

    # Error Handling for file operations
    try:
        # Save the raw images to raw_img_path
        file.save(os.path.join(raw_img_path, filename))
        constituents = file.filename.split("_")
        obstacle_id = constituents[1]

        # Load image from the raw_img_path
        frame = cv2.imread(os.path.join(raw_img_path, filename)) 
    except: 
        print("Unexpected error occured!")
        result = {
            "obstacle_id": obstacle_id,
            "image_id": 23
        }
        return jsonify(result)      

    # Run image recognition on the image
    results = robomodel.infer(image = frame, confidence = 0.5, iou_threshold=0.5)
    detections = sv.Detections.from_inference(results[0].dict(by_alias=True, exclude_none=True))

    if not detections.data:
        print("Failed to detect image_id from the image")
        return jsonify({
            "obstacle_id": obstacle_id,
            "image_id": 23
        })

    # DEBUGGING PRINT STATEMENTS
    print("Detected image:", detections.data)

    image_data = detections.data['class_name'][0]
    image_id = int(image_data[2:])

    # Create supervision annotators
    bounding_box_annotator = sv.BoundingBoxAnnotator()
    label_annotator = sv.LabelAnnotator()

    # Annotate the frame
    bounded_frame = bounding_box_annotator.annotate(scene=frame, detections=detections)
    annotated_frame = label_annotator.annotate(scene=bounded_frame, detections=detections)

    # Generate a unique filename for the annotated image
    rand = random.randint(1000, 9999)
    annotated_filename = f"{annotated_img_path}/annotated_image_{image_data}_{rand}.jpg"
    
    try:
        # Save the annotated image
        cv2.imwrite(annotated_filename, annotated_frame)
    except:
        print("Unexpected error occured when trying to save annotated image!")
    finally:
        # Return the obstacle_id and image_id
        result = {
            "obstacle_id": obstacle_id,
            "image_id": image_id
        }
    return jsonify(result)