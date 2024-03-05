
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
    :return: a json object with a key "result" and value a dictionary with keys "obstacle_id" and "image_id"
    """
    print(f"Request: {request.files}")
    file = request.files['file']
    filename = file.filename

    # Initialise folders
    setup_img_folders()
    clear_images()

    file.save(os.path.join('images', filename))
    # filename format: "<timestamp>_<obstacle_id>_<signal>.jpeg"
    constituents = file.filename.split("_")
    # print ("Constituents: ", constituents)
    obstacle_id = constituents[1]

    # print(f"file: {file}")
    frame = cv2.imread(os.path.join('images', filename))  

    if frame is None:
        print("Failed to load image")
        result = {
            "obstacle_id": 1,
            "image_id": 23
        }

    else:
        results = robomodel.infer(image = frame,
                                  confidence = 0.5,
                                  iou_threshold=0.5)
        detections = sv.Detections.from_inference(results[0].dict(by_alias=True, exclude_none=True))

        class_name = detections.data['class_name'][0]
        numeric_part = ''.join(filter(str.isdigit, class_name))
        image_id = int(numeric_part)  # Convert the extracted numeric part to an integer

        # Annotate the frame
        bounding_box_annotator = sv.BoundingBoxAnnotator()
        label_annotator = sv.LabelAnnotator()
        # Create supervision annotators
        annotated_frame = bounding_box_annotator.annotate(scene=frame, detections=detections)
        annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=detections)

        # Generate a unique filename for the annotated image
        rand = random.randint(1000, 9999)
        annotated_filename = f"own_results/annotated_image_{class_name}_{rand}.jpg"
        
        # Save the annotated image
        cv2.imwrite(annotated_filename, annotated_frame)


        # print("detections:", detections)
        # print("image:",image_id)

        ## Week 9 ## 
        # We don't need to pass in the signal anymore
        # image_id = predict_image_week_9(filename,model)

        # Return the obstacle_id and image_id
        result = {
            "obstacle_id": obstacle_id,
            "image_id": image_id
        }
    return jsonify(result)