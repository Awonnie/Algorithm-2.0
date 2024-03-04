# Third Party Imports
from flask import Blueprint, request, jsonify
import cv2
from inference import get_roboflow_model
import supervision as sv

# Built-in Imports
import os

# Local Imports
from consts import MODEL_ID, CV_API_KEY

image = Blueprint('image', __name__)
# Initialise model
robomodel = get_roboflow_model(model_id= MODEL_ID, api_key=CV_API_KEY) 

@image.route('/image', methods=['POST'])
def image_predict():
    """
    FLASK ROUTE: IMAGE RECOGNITION
    This is the main endpoint for the image prediction algorithm

    Return: a json object with a key "result" and value a dictionary with keys "obstacle_id" and "image_id"
    """
    file = request.files['file']
    filename = file.filename
    file.save(os.path.join('uploads', filename))
    # filename format: "<timestamp>_<obstacle_id>_<signal>.jpeg"
    constituents = file.filename.split("_")
    print ("Constituents: ", constituents)
    obstacle_id = constituents[1]

    frame = cv2.imread(os.path.join('uploads', filename))  

    if frame is None:
        print("Failed to load image")
        result = {
            "obstacle_id": 1,
            "image_id": 40
        }

    else:
        results = robomodel.infer(frame)
        detections = sv.Detections.from_inference(results[0].dict(by_alias=True, exclude_none=True))

        class_name = int(detections.data.get('class_name'))
        numeric_part = ''.join(filter(str.isdigit, class_name))
        image_id = int(numeric_part)  # Convert the extracted numeric part to an integer

        print("detections:", detections)
        print("image:",image_id)

        result = {
            "obstacle_id": obstacle_id,
            "image_id": image_id
        }
    return jsonify(result)