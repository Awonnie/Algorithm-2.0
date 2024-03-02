from consts import GRID_HEIGHT, GRID_WIDTH
from direction import Direction

def coordinate_cal(path_results, command, i):
    # if command is snap
    if command.startswith("SNAP"):
        present = path_results[i].copy()
        present['s'] = 1
        i += 1
        path_results.append(present)
        return path_results, i
    
    # if command is forward
    if command.startswith("FW") or command.startswith("FS") or command.startswith("BW") or command.startswith("BS"):
        # calculate distance
        distance = int(command[2:])//10
        # assign direction of travel
        robot_direction = path_results[i]['d']
        if robot_direction == 0:
            axis, direction = 'y', 1
        elif robot_direction == 4:
            axis, direction = 'y', -1
        elif robot_direction == 2:
            axis, direction = 'x', 1
        elif robot_direction == 6:
            axis, direction = 'x', -1
        # reverse instructions if command is backward
        if command.startswith("BW") or command.startswith("BS"):
            reverse = -1
        else:
            reverse = 1
        # add each step along direction of travel    
        for add_this in range(0, distance):
            present = path_results[i].copy()
            i+=1
            if axis == 'x':
                present['x'] = present['x'] + (1*direction *reverse)
            elif axis == 'y':
                present['y'] = present['y'] + (1*direction*reverse)
            present['s'] = -1
            path_results.append(present)
        return path_results, i
    
    # if command is to turn backwards, BR00 = BW30 + 90 anticlockwise (d - 2) + BW10, BL00 = BW30 + 90 clockwise (d + 2) + BW10
    if command.startswith("BR") or command.startswith("BL"):
        # assign steps moving backward
        path_results, i = coordinate_cal(path_results, "BW30", i)
        # assign turn direction
        if command.startswith("BR"):
            turn = -2
        else:
            turn = 2
        # assign turn step
        present = path_results[i].copy()
        i+=1
        present['d'] = present['d'] + turn
        if present['d'] == 8:
            present['d'] = 0
        elif present['d'] == -2:
            present['d'] = 6
        present['s'] = -1
        path_results.append(present)
        # assign step moving backward
        path_results, i = coordinate_cal(path_results, "BW10", i)
        return path_results, i

    # if command is to turn forwards, FR00 = FW10 + 90 clockwise (d + 2) + FW30, FL00 = FW10 + 90 anticlockwise (d + 2) + FW30
    if command.startswith("FR") or command.startswith("FL"):
        # assign steps moving forward
        path_results, i = coordinate_cal(path_results, "FW10", i)
        # assign turn direction
        if command.startswith("FR"):
            turn = 2
        else:
            turn = -2
        # assign turn step
        present = path_results[i].copy()
        i+=1
        present['d'] = present['d'] + turn        
        if present['d'] == 8:
            present['d'] = 0
        elif present['d'] == -2:
            present['d'] = 6
        present['s'] = -1
        path_results.append(present)    
        # assign steps moving forward
        path_results, i = coordinate_cal(path_results, "FW30", i)
        return path_results, i    
    
    return path_results, i    

def command_generator(states, obstacles):
    """
    This function takes in a list of states and generates a list of commands for the robot to follow
    
    Inputs
    ------
    states: list of State objects
    obstacles: list of obstacles, each obstacle is a dictionary with keys "x", "y", "d", and "id"

    Returns
    -------
    commands: list of commands for the robot to follow
    """

    # Convert the list of obstacles into a dictionary with key as the obstacle id and value as the obstacle
    obstacles_dict = {ob['id']: ob for ob in obstacles}
    
    # Initialize commands list
    commands = []

    # Iterate through each state in the list of states
    for i in range(1, len(states)):
        steps = "00"

        # If previous state and current state are the same direction,
        if states[i].direction == states[i - 1].direction:
            # Forward - Must be (east facing AND x value increased) OR (north facing AND y value increased)
            if (states[i].x > states[i - 1].x and states[i].direction == Direction.EAST) or (states[i].y > states[i - 1].y and states[i].direction == Direction.NORTH):
                commands.append("FW10")
            # Forward - Must be (west facing AND x value decreased) OR (south facing AND y value decreased)
            elif (states[i].x < states[i-1].x and states[i].direction == Direction.WEST) or (
                    states[i].y < states[i-1].y and states[i].direction == Direction.SOUTH):
                commands.append("FW10")
            # Backward - All other cases where the previous and current state is the same direction
            else:
                commands.append("BW10")

            # If any of these states has a valid screenshot ID, then add a SNAP command as well to take a picture
            if states[i].screenshot_id != -1:
                # NORTH = 0
                # EAST = 2
                # SOUTH = 4
                # WEST = 6

                current_ob_dict = obstacles_dict[states[i].screenshot_id] # {'x': 9, 'y': 10, 'd': 6, 'id': 9}
                current_robot_position = states[i] # {'x': 1, 'y': 8, 'd': <Direction.NORTH: 0>, 's': -1}

                # Obstacle facing WEST, robot facing EAST
                if current_ob_dict['d'] == 6 and current_robot_position.direction == 2:
                    if current_ob_dict['y'] > current_robot_position.y:
                        commands.append(f"SNAP{states[i].screenshot_id}_L")
                    elif current_ob_dict['y'] == current_robot_position.y:
                        commands.append(f"SNAP{states[i].screenshot_id}_C")
                    elif current_ob_dict['y'] < current_robot_position.y:
                        commands.append(f"SNAP{states[i].screenshot_id}_R")
                    else:
                        commands.append(f"SNAP{states[i].screenshot_id}")
                
                # Obstacle facing EAST, robot facing WEST
                elif current_ob_dict['d'] == 2 and current_robot_position.direction == 6:
                    if current_ob_dict['y'] > current_robot_position.y:
                        commands.append(f"SNAP{states[i].screenshot_id}_R")
                    elif current_ob_dict['y'] == current_robot_position.y:
                        commands.append(f"SNAP{states[i].screenshot_id}_C")
                    elif current_ob_dict['y'] < current_robot_position.y:
                        commands.append(f"SNAP{states[i].screenshot_id}_L")
                    else:
                        commands.append(f"SNAP{states[i].screenshot_id}")

                # Obstacle facing NORTH, robot facing SOUTH
                elif current_ob_dict['d'] == 0 and current_robot_position.direction == 4:
                    if current_ob_dict['x'] > current_robot_position.x:
                        commands.append(f"SNAP{states[i].screenshot_id}_L")
                    elif current_ob_dict['x'] == current_robot_position.x:
                        commands.append(f"SNAP{states[i].screenshot_id}_C")
                    elif current_ob_dict['x'] < current_robot_position.x:
                        commands.append(f"SNAP{states[i].screenshot_id}_R")
                    else:
                        commands.append(f"SNAP{states[i].screenshot_id}")

                # Obstacle facing SOUTH, robot facing NORTH
                elif current_ob_dict['d'] == 4 and current_robot_position.direction == 0:
                    if current_ob_dict['x'] > current_robot_position.x:
                        commands.append(f"SNAP{states[i].screenshot_id}_R")
                    elif current_ob_dict['x'] == current_robot_position.x:
                        commands.append(f"SNAP{states[i].screenshot_id}_C")
                    elif current_ob_dict['x'] < current_robot_position.x:
                        commands.append(f"SNAP{states[i].screenshot_id}_L")
                    else:
                        commands.append(f"SNAP{states[i].screenshot_id}")
            continue

        # If previous state and current state are not the same direction, it means that there will be a turn command involved
        # Assume there are 4 turning command: FR, FL, BL, BR (the turn command will turn the robot 90 degrees)
        # FR00 | FR30: Forward Right;
        # FL00 | FL30: Forward Left;
        # BR00 | BR30: Backward Right;
        # BL00 | BL30: Backward Left;

        # Facing north previously
        if states[i - 1].direction == Direction.NORTH:
            # Facing east afterwards
            if states[i].direction == Direction.EAST:
                # y value increased -> Forward Right
                if states[i].y > states[i - 1].y:
                    commands.append("FR{}".format(steps))
                # y value decreased -> Backward Left
                else:
                    commands.append("BL{}".format(steps))
            # Facing west afterwards
            elif states[i].direction == Direction.WEST:
                # y value increased -> Forward Left
                if states[i].y > states[i - 1].y:
                    commands.append("FL{}".format(steps))
                # y value decreased -> Backward Right
                else:
                    commands.append("BR{}".format(steps))
            else:
                raise Exception("Invalid turing direction")

        elif states[i - 1].direction == Direction.EAST:
            if states[i].direction == Direction.NORTH:
                if states[i].y > states[i - 1].y:
                    commands.append("FL{}".format(steps))
                else:
                    commands.append("BR{}".format(steps))

            elif states[i].direction == Direction.SOUTH:
                if states[i].y > states[i - 1].y:
                    commands.append("BL{}".format(steps))
                else:
                    commands.append("FR{}".format(steps))
            else:
                raise Exception("Invalid turing direction")

        elif states[i - 1].direction == Direction.SOUTH:
            if states[i].direction == Direction.EAST:
                if states[i].y > states[i - 1].y:
                    commands.append("BR{}".format(steps))
                else:
                    commands.append("FL{}".format(steps))
            elif states[i].direction == Direction.WEST:
                if states[i].y > states[i - 1].y:
                    commands.append("BL{}".format(steps))
                else:
                    commands.append("FR{}".format(steps))
            else:
                raise Exception("Invalid turing direction")

        elif states[i - 1].direction == Direction.WEST:
            if states[i].direction == Direction.NORTH:
                if states[i].y > states[i - 1].y:
                    commands.append("FR{}".format(steps))
                else:
                    commands.append("BL{}".format(steps))
            elif states[i].direction == Direction.SOUTH:
                if states[i].y > states[i - 1].y:
                    commands.append("BR{}".format(steps))
                else:
                    commands.append("FL{}".format(steps))
            else:
                raise Exception("Invalid turing direction")
        else:
            raise Exception("Invalid position")

        # If any of these states has a valid screenshot ID, then add a SNAP command as well to take a picture
        if states[i].screenshot_id != -1:  
            # NORTH = 0
            # EAST = 2
            # SOUTH = 4
            # WEST = 6

            current_ob_dict = obstacles_dict[states[i].screenshot_id] # {'x': 9, 'y': 10, 'd': 6, 'id': 9}
            current_robot_position = states[i] # {'x': 1, 'y': 8, 'd': <Direction.NORTH: 0>, 's': -1}

            # Obstacle facing WEST, robot facing EAST
            if current_ob_dict['d'] == 6 and current_robot_position.direction == 2:
                if current_ob_dict['y'] > current_robot_position.y:
                    commands.append(f"SNAP{states[i].screenshot_id}_L")
                elif current_ob_dict['y'] == current_robot_position.y:
                    commands.append(f"SNAP{states[i].screenshot_id}_C")
                elif current_ob_dict['y'] < current_robot_position.y:
                    commands.append(f"SNAP{states[i].screenshot_id}_R")
                else:
                    commands.append(f"SNAP{states[i].screenshot_id}")
            
            # Obstacle facing EAST, robot facing WEST
            elif current_ob_dict['d'] == 2 and current_robot_position.direction == 6:
                if current_ob_dict['y'] > current_robot_position.y:
                    commands.append(f"SNAP{states[i].screenshot_id}_R")
                elif current_ob_dict['y'] == current_robot_position.y:
                    commands.append(f"SNAP{states[i].screenshot_id}_C")
                elif current_ob_dict['y'] < current_robot_position.y:
                    commands.append(f"SNAP{states[i].screenshot_id}_L")
                else:
                    commands.append(f"SNAP{states[i].screenshot_id}")

            # Obstacle facing NORTH, robot facing SOUTH
            elif current_ob_dict['d'] == 0 and current_robot_position.direction == 4:
                if current_ob_dict['x'] > current_robot_position.x:
                    commands.append(f"SNAP{states[i].screenshot_id}_L")
                elif current_ob_dict['x'] == current_robot_position.x:
                    commands.append(f"SNAP{states[i].screenshot_id}_C")
                elif current_ob_dict['x'] < current_robot_position.x:
                    commands.append(f"SNAP{states[i].screenshot_id}_R")
                else:
                    commands.append(f"SNAP{states[i].screenshot_id}")

            # Obstacle facing SOUTH, robot facing NORTH
            elif current_ob_dict['d'] == 4 and current_robot_position.direction == 0:
                if current_ob_dict['x'] > current_robot_position.x:
                    commands.append(f"SNAP{states[i].screenshot_id}_R")
                elif current_ob_dict['x'] == current_robot_position.x:
                    commands.append(f"SNAP{states[i].screenshot_id}_C")
                elif current_ob_dict['x'] < current_robot_position.x:
                    commands.append(f"SNAP{states[i].screenshot_id}_L")
                else:
                    commands.append(f"SNAP{states[i].screenshot_id}")

    # Final command is the stop command (FIN)
    commands.append("FIN")  

    # Compress commands if there are consecutive forward or backward commands
    compressed_commands = [commands[0]]

    for i in range(1, len(commands)):
        # If both commands are BW
        if commands[i].startswith("BW") and compressed_commands[-1].startswith("BW"):
            # Get the number of steps of previous command
            steps = int(compressed_commands[-1][2:])
            # If steps are not 90, add 10 to the steps
            if steps != 90:
                compressed_commands[-1] = "BW{}".format(steps + 10)
                continue

        # If both commands are FW
        elif commands[i].startswith("FW") and compressed_commands[-1].startswith("FW"):
            # Get the number of steps of previous command
            steps = int(compressed_commands[-1][2:])
            # If steps are not 90, add 10 to the steps
            if steps != 90:
                compressed_commands[-1] = "FW{}".format(steps + 10)
                continue
        
        # Otherwise, just add as usual
        compressed_commands.append(commands[i])

    return compressed_commands
