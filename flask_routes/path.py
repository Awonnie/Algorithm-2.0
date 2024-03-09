import time

from flask import Blueprint, jsonify, request

# Local Imports
from arena_objects import Arena, Obstacle, Robot
from consts import ROBOT_SPEED
from path_finding import PathFinder, command_generator, coordinate_cal
from .helper import clear_images, setup_img_folders

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

    # DEBUGGING PRINT STATEMENTS
    print("Obstacles received:")
    for ob in obstacles:
        print(f"{ob['id']}: {(ob['x'], ob['y'], ob['d'])}")

    # Initialize the Arena, Robot and Obstacles
    robot = Robot(robot_x, robot_y, robot_direction)
    arena = Arena(arena_height=20, arena_width=20, robot=robot)
    for ob in obstacles:
        obstacle_to_add = Obstacle(ob['x'], ob['y'], ob['d'], ob['id'])
        arena.add_obstacle(obstacle_to_add)

    # Creates the PathFinder object
    path_finder = PathFinder(arena, big_turn=None)

    # Get shortest path
    search_start_time = time.perf_counter()
    optimal_path, total_distance = path_finder.get_shortest_path(retrying=retrying)
    search_end_time = time.perf_counter()
    
    # Based on the shortest path, generate commands for the robot
    commands = command_generator(optimal_path, obstacles)

    # Initialise folders to prepare for SNAP commands
    setup_img_folders()
    clear_images()

    # Used to store the estimated duration in seconds for running each command
    path_results = []
    for path in optimal_path:
        path_results.append(path.get_dict())

    path_execution_time = []
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
    total_duration = sum(path_execution_time)

    # DEBUGGING PRINT STATEMENTS
    print(f"Time taken to find shortest path using A* search: {search_end_time - search_start_time:0.4f}s")
    print(f"Distance to travel: {total_distance} units")
    print("Commands:")    
    for command in commands:
        if command.startswith("SNAP"):
            print(command)
        else:
            print(command, end=" ")
        
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