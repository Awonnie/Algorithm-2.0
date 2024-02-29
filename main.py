import time

import cv2
import supervision as sv
from flask import Flask, jsonify, request
from flask_cors import CORS
from inference import get_roboflow_model

from algo.algo import MazeSolver
from consts import MOTOR_SPEED
from helper import command_generator, coordinate_cal
from model import *

# import a utility function for loading Roboflow models
robomodel = get_roboflow_model(model_id= "mdp_grp27/3", api_key="8knDdTJZg79rGzgli7Ub") 


app = Flask(__name__)
CORS(app)
#model = load_model()
model = None

@app.route('/status', methods=['GET'])
def status():
    """
    This is a health check endpoint to check if the server is running
    :return: a json object with a key "result" and value s"ok"
    """
    return jsonify({"result": "ok"})


@app.route('/path', methods=['POST'])
def path_finding():
    """
    This is the main endpoint for the path finding algorithm
    :return: a json object with a key "data" and value a dictionary with keys "distance", "path", and "commands"
    """
    # Get the json data from the request
    content = request.json

    # Get the obstacles, big_turn, retrying, robot_x, robot_y, and robot_direction from the json data
    obstacles = content['obstacles']
    # big_turn = int(content['big_turn'])
    retrying = content['retrying']
    robot_x, robot_y = content['robot_x'], content['robot_y']
    robot_direction = int(content['robot_dir'])

    # Initialize MazeSolver object with robot size of 20x20, bottom left corner of robot at (1,1), facing north, and whether to use a big turn or not.
    maze_solver = MazeSolver(20, 20, robot_x, robot_y, robot_direction, big_turn=None)

    # Add each obstacle into the MazeSolver. Each obstacle is defined by its x,y positions, its direction, and its id
    for ob in obstacles:
        maze_solver.add_obstacle(ob['x'], ob['y'], ob['d'], ob['id'])

    start = time.time()
    # Get shortest path
    optimal_path, distance = maze_solver.get_optimal_order_dp(retrying=retrying)
    print(f"Time taken to find shortest path using A* search: {time.time() - start}s")
    print(f"Distance to travel: {distance} units")
    
    # Based on the shortest path, generate commands for the robot
    commands = command_generator(optimal_path, obstacles)

    # Get the starting location and add it to path_results
    path_results = [optimal_path[0].get_dict()]
    
    # Used to store the estimated duration in seconds for running each command
    path_time = []

    # Initialize total duration variable
    total_duration = 0

    # Process each command individually and append the location the robot should be after executing that command to path_results
    i = 0
    command_duration = 0
    for command in commands:
        path_results, i = coordinate_cal(path_results, command, i)

    # Initialize total duration variable
    total_duration = 0

    # Process each command individually and append the location the robot should be after executing that command to path_results
    i = 0
    for command in commands:
        command_duration = 0
        movement = 0
        if command.startswith("SNAP"):
            movement = 0
            command_duration = distance
            continue

        if command.startswith("FIN"):
            movement = 0
            command_duration = distance
            continue

        elif command.startswith("FW") or command.startswith("FS"):
            i += int(command[2:]) // 10
            movement = int(command[2:])/10
            command_duration = movement / MOTOR_SPEED

        elif command.startswith("BW") or command.startswith("BS"):
            i += int(command[2:]) // 10
            command_duration = 2

        else:
            i += 1
            command_duration = 2

        total_duration += command_duration

    for i in range(len(path_results)):
        if (i+1) == len(path_results): 
            break

        if (path_results[i].get('s')==1):
            path_time.append(2.0)

        path_time.append(MazeSolver.compute_coord_distance(
            path_results[i].get('x'), path_results[i].get('y'),
            path_results[i+1].get('x'), path_results[i+1].get('y')
            ) / MOTOR_SPEED)
        
        

    path_time.insert(0,0)
    print(f"Path: {path_results}")
    print(f"Path Time: {path_time}")
    print(f"Path: {path_results}")
    print(f"Commands: {commands}")
    print(f"Duration:{total_duration}")
    
    return jsonify({
        "data": {
            'distance': distance,
            'path': path_results,
            'commands': commands,
            'path_time': path_time,
            'duration': total_duration 
        },
        "error": None
    })


@app.route('/image', methods=['POST'])
def image_predict():
    """
    This is the main endpoint for the image prediction algorithm
    :return: a json object with a key "result" and value a dictionary with keys "obstacle_id" and "image_id"
    """
    file = request.files['file']
    filename = file.filename
    file.save(os.path.join('uploads', filename))
    # filename format: "<timestamp>_<obstacle_id>_<signal>.jpeg"
    constituents = file.filename.split("_")
    print ("Constituents: ", constituents)
    obstacle_id = constituents[1]

    # Perform inference on the saved image, might have to change the file path to just (filename)
    #frame = cv2.imread(os.path.join(filename))  
    #for testing only
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

        class_name = int(detections.data.get['class_name'])
        numeric_part = ''.join(filter(str.isdigit, class_name))
        image_id = int(numeric_part)  # Convert the extracted numeric part to an integer

        print("detections:", detections)
        print("image:",image_id)

        ## Week 9 ## 
        # We don't need to pass in the signal anymore
        #image_id = predict_image_week_9(filename,model)

        # Return the obstacle_id and image_id
        result = {
            "obstacle_id": obstacle_id,
            "image_id": image_id
        }
    return jsonify(result)



# @app.route('/image', methods=['POST'])
# def image_predict():
#     """
#     This is the main endpoint for the image prediction algorithm
#     :return: a json object with a key "result" and value a dictionary with keys "obstacle_id" and "image_id"
#     """
#     file = request.files['file']
#     filename = file.filename
#     file.save(os.path.join('uploads', filename))
#     # filename format: "<timestamp>_<obstacle_id>_<signal>.jpeg"
#     constituents = file.filename.split("_")
#     print ("Constituents: ", constituents)
#     obstacle_id = constituents[1]

#     # Perform inference on the saved image, might have to change the file path to just (filename)
#     #frame = cv2.imread(os.path.join(filename))  
#     #for testing only
#     frame = cv2.imread(os.path.join('uploads', filename))  

#     if frame is None:
#         print("Failed to load image")
#         result = {
#             "obstacle_id": 1,
#             "image_id": 40
#         }

#     else:
#         results = robomodel.infer(frame)
#         detections = sv.Detections.from_inference(results[0].dict(by_alias=True, exclude_none=True))
#         image_id = int(detections.class_id[0])
#         print("detections:", detections)

#         # Return the obstacle_id and image_id
#         result = {
#             "obstacle_id": obstacle_id,
#             "image_id": image_id
#         }
#     return jsonify(result)


@app.route('/stitch', methods=['GET'])
def stitch():
    """
    This is the main endpoint for the stitching command. Stitches the images using two different functions, in effect creating two stitches, just for redundancy purposes
    """
    img = stitch_image()
    img.show()
    img2 = stitch_image_own()
    img2.show()
    return jsonify({"result": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
