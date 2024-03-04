# Third Party Imports
import os
# Built-in Imports
import time

from flask import Blueprint, jsonify, request

# Local Imports
from arena_objects import Arena, Obstacle, Robot
from consts import ROBOT_SPEED
from path_finding import PathFinder, command_generator, coordinate_cal

path = Blueprint('path', __name__)

@path.route('/path', methods=['POST'])
def path_finder():
    """
    FLASK ROUTE: PATH FINDER
    This is the main endpoint for the path finding algorithm

    Return: a json object with a key "data" and value a dictionary with keys "distance", "path", and "commands"
    """
    # Get the json data from the request
    content = request.json

    # Get the obstacles, big_turn, retrying, robot_x, robot_y, and robot_direction from the json data
    obstacles = content['obstacles']
    retrying = content['retrying']
    robot_x, robot_y = content['robot_x'], content['robot_y']
    robot_direction = int(content['robot_dir'])

    # Initialize the Arena, Robot and Obstacles
    robot = Robot(robot_x, robot_y, robot_direction)
    arena = Arena(arena_height=20, arena_width=20, robot=robot)
    for ob in obstacles:
        obstacle_to_add = Obstacle(ob['x'], ob['y'], ob['d'], ob['id'])
        arena.add_obstacle(obstacle_to_add)

    # Creates the PathFinder object
    path_finder = PathFinder(arena, big_turn=None)

    search_start_time = time.time()
    # Get shortest path
    optimal_path, total_distance = path_finder.get_shortest_path(retrying=retrying)
    print(f"Time taken to find shortest path using A* search: {time.time() - search_start_time}s")
    print(f"Distance to travel: {total_distance} units")
    
    # Based on the shortest path, generate commands for the robot
    commands = command_generator(optimal_path, obstacles)
    
    # Process each command individually and append the location the robot should be after executing that command to path_results
    i = 0
    path_results = [optimal_path[0].get_dict()] # Get the starting location and add it to path_results
    for command in commands:
        path_results, i = coordinate_cal(path_results, command, i)

    # Used to store the estimated duration in seconds for running each command
    path_execution_time = []

    # Process each command individually and append the location the robot should be after executing that command to path_results
    total_duration = 0
    for command in commands:
        command_duration = 0
        movement = 0

        if command.startswith("FIN"):
            continue

        if command.startswith("SNAP"):
            command_duration = 1
            continue

        elif command.startswith("FW") or command.startswith("BW"):
            movement = int(command[2:]) // 10
            command_duration = movement / ROBOT_SPEED

        else:   # This covers all rotation movements
            command_duration = 3
        
        total_duration += command_duration

    for i in range(len(path_results)):
        if (i+1) == len(path_results): 
            break

        if (path_results[i].get('s')==1):
            path_execution_time.append(2.0)

        path_execution_time.append(path_finder._PathFinder__compute_distance_between(
            x1 = path_results[i].get('x'), y1 = path_results[i].get('y'),
            x2 = path_results[i+1].get('x'), y2 = path_results[i+1].get('y')
            ) / ROBOT_SPEED)
        
    path_execution_time.insert(0,0)

    # print(f"Path: {path_results}")
    # print(f"Path Execution Time: {path_execution_time}")
    print(f"Commands: {commands}")
    # print(f"Duration:{total_duration}")

    for filename in os.listdir('own_results'):
        if filename.endswith(".jpg"):
            file_path = os.path.join('own_results',filename)
            os.remove(file_path)

    for filename in os.listdir('uploads'):
        if filename.endswith(".jpg"):
            file_path = os.path.join('uploads',filename)
            os.remove(file_path)

    for filename in os.listdir('uploads/originals'):
        if filename.endswith(".jpg"):
            file_path = os.path.join('uploads/originals',filename)
            os.remove(file_path)
    
    return jsonify({
        "data": {
            'distance': total_distance,
            'path': path_results,
            'commands': commands,
            'path_execution_time': path_execution_time,
            'duration': total_duration
        },
        "error": None
    })