import heapq
import math
from typing import List

import numpy as np
from python_tsp.exact import solve_tsp_dynamic_programming

from arena_objects import GridCell
from consts import ITERATIONS, SAFE_COST, TURN_FACTOR, TURN_RADIUS
from direction import Direction

movement_directions = [
    (1, 0, Direction.EAST),
    (-1, 0, Direction.WEST),
    (0, 1, Direction.NORTH),
    (0, -1, Direction.SOUTH),
]

class PathFinder:
    def __init__(
            self,
            arena,
            big_turn=None # the big_turn here is to allow 3-1 turn(0 - by default) | 4-2 turn(1)
    ):
        # Initialize a Arena object for the arena representation
        self.arena = arena
        # Initialize a Robot object for robot representation
        self.robot = arena.get_robot()
        # Create tables for paths and costs
        self.path_table = dict()
        self.cost_table = dict()
        if big_turn is None:
            self.big_turn = 0
        else:
            self.big_turn = int(big_turn)

    def __calc_rotation_cost(self, d1, d2):
        diff = abs(d1 - d2)
        return min(diff, 8 - diff)

    def __compute_distance_between(
            self, 
            start_state: GridCell = None, 
            end_state: GridCell = None, 
            x1: int = None, 
            y1: int = None, 
            x2: int = None, 
            y2: int = None, 
            level = 1
            ):
        """Compute the L-n distance between two cell states

        Args:
            start_state (GridCell): Start cell state
            end_state (GridCell): End cell state
            level (int, optional): L-n distance to compute. Defaults to 1.

        Returns:
            float: L-n distance between the two given cell states
        """
        if not start_state and not end_state:
            horizontal_distance = x1 - x2
            vertical_distance = y1 - y2
        else:
            horizontal_distance = start_state.x - end_state.x
            vertical_distance = start_state.y - end_state.y


        # Euclidean distance
        if level == 2:
            return math.sqrt(horizontal_distance ** 2 + vertical_distance ** 2)

        return abs(horizontal_distance) + abs(vertical_distance)

    def __get_binary_strings(self, n):
        """Generate all possible n-digit binary strings

        Args:
            n (int): number of digits in binary string to generate

        Returns:
            List: list of all possible n-digit binary strings
        """
        s = []
        l = bin(2 ** n - 1).count('1')

        for i in range(2 ** n):
            s.append(bin(i)[2:].zfill(l))

        s.sort(key=lambda x: x.count('1'), reverse=True)
        return s

    def get_shortest_path(self, retrying) -> List[GridCell]:
        '''
        Main Function to calculate the shortest path to go to all obstacles once

        Args:
            retrying (boolean): Whether or not the robot needs to retry

        Returns:
            optimal_path (List):   List of paths for the robot to follow
            total_distance (int):   Total Distance required to travel in units
        '''
        total_distance = 1e9
        optimal_path = []

        # Get all possible positions that can view the obstacles
        all_view_positions = self.arena.get_viewing_positions(retrying)

        for op in self.__get_binary_strings(len(all_view_positions)):
            # op is binary string of length len(all_view_positions) == len(obstacles)
            # If index == 1 means the view_positions[index] is selected to visit, otherwise drop

            # Initialize `items` to be a list containing the robot's start state as the first item
            items = [self.robot.get_robot_cell()]
            # Initialize `cur_view_positions` to be an empty list
            cur_view_positions = []
            
            for idx in range(len(all_view_positions)):
                if op[idx] == '1':
                    items = items + all_view_positions[idx]
                    cur_view_positions.append(all_view_positions[idx])

            self.__path_cost_generator(items)
            combination = []
            self.__generate_combination(cur_view_positions, 0, [], combination, [ITERATIONS])

            for c in combination: # run the algo some times ->
                visited_candidates = [0] # add the start state of the robot

                cur_index = 1
                fixed_cost = 0 # the cost applying for the position taking obstacle pictures
                for index, view_position in enumerate(cur_view_positions):
                    visited_candidates.append(cur_index + c[index])
                    fixed_cost += view_position[c[index]].penalty
                    cur_index += len(view_position)
                
                cost_np = np.zeros((len(visited_candidates), len(visited_candidates)))

                for s in range(len(visited_candidates) - 1):
                    for e in range(s + 1, len(visited_candidates)):
                        u = items[visited_candidates[s]]
                        v = items[visited_candidates[e]]
                        if (u, v) in self.cost_table.keys():
                            cost_np[s][e] = self.cost_table[(u, v)]
                        else:
                            cost_np[s][e] = 1e9
                        cost_np[e][s] = cost_np[s][e]
                cost_np[:, 0] = 0
                _permutation, _distance = solve_tsp_dynamic_programming(cost_np)
                if _distance + fixed_cost >= total_distance:
                    continue

                optimal_path = [items[0]]
                total_distance = _distance + fixed_cost

                for i in range(len(_permutation) - 1):
                    from_item = items[visited_candidates[_permutation[i]]]
                    to_item = items[visited_candidates[_permutation[i + 1]]]

                    cur_path = self.path_table[(from_item, to_item)]
                    for j in range(1, len(cur_path)):
                        optimal_path.append(GridCell(cur_path[j][0], cur_path[j][1], cur_path[j][2]))

                    optimal_path[-1].set_screenshot(to_item.screenshot_id)

            if optimal_path:
                # if found optimal path, return
                break
            
        return optimal_path, total_distance

    def __generate_combination(self, view_positions, index, current, result, iterations_left):
        if index == len(view_positions):
            result.append(current[:])
            return

        if iterations_left[0] == 0:
            return

        iterations_left[0] -= 1
        for j in range(len(view_positions[index])):
            current.append(j)
            self.__generate_combination(view_positions, index + 1, current, result, iterations_left)
            current.pop()

    def __get_safe_cost(self, x, y):
        """Get the safe cost of a particular x,y coordinate wrt obstacles that are exactly 2 units away from it in both x and y directions

        Args:
            x (int): x-coordinate
            y (int): y-coordinate

        Returns:
            int: safe cost
        """
        for ob in self.arena.obstacles:
            if abs(ob.x-x) == 2 and abs(ob.y-y) == 2:
                return SAFE_COST
            
            if abs(ob.x-x) == 1 and abs(ob.y-y) == 2:
                return SAFE_COST
            
            if abs(ob.x-x) == 2 and abs(ob.y-y) == 1:
                return SAFE_COST

        return 0

      
    def __get_neighbors(self, x, y, orientation, strict=True):  # TODO: see the behavior of the robot and adjust...
        """
        Return a list of tuples with format:
        newX, newY, new_direction
        """
        # Neighbors have the following format: {newX, newY, movement direction, safe cost}
        # Neighbors are coordinates that fulfill the following criteria:
        # If moving in the same direction:
        #   - Valid position within bounds
        #   - Must be at least 4 units away in total (x+y) 
        #   - Furthest distance must be at least 3 units away (x or y)
        # If it is exactly 2 units away in both x and y directions, safe cost = SAFECOST. Else, safe cost = 0

        neighbors = []
        # Assume that after following this direction, the car direction is EXACTLY md
        for dx, dy, new_orientation in movement_directions:
            if orientation == new_orientation:  # if the new direction == md
                # Check for valid position
                if self.arena.is_reachable(x + dx, y + dy):  # Move Foward;
                    # Get safe cost of destination
                    safe_cost = self.__get_safe_cost(x + dx, y + dy)
                    neighbors.append((x + dx, y + dy, new_orientation, safe_cost))
                # Check for valid position
                if self.arena.is_reachable(x - dx, y - dy):  # Move Backward;
                    # Get safe cost of destination
                    safe_cost = self.__get_safe_cost(x - dx, y - dy)
                    neighbors.append((x - dx, y - dy, new_orientation, safe_cost))

            else:  # consider 8 cases

                if not self.arena.is_reachable(x, y, preTurn=True):
                    continue
                
                # Turning radius can be found in consts.py: set to (3,1)
                bigger_change = max(TURN_RADIUS)
                smaller_change = min(TURN_RADIUS)

                if orientation == Direction.NORTH:
                    # Facing NORTH -> Facing EAST
                    if new_orientation == Direction.EAST:
                        forward_x = x + bigger_change
                        forward_y = y + smaller_change
                        reverse_x = x - bigger_change
                        reverse_y = y - smaller_change

                        # Corresponding Command: FR00
                        if self.arena.is_reachable(forward_x + 1, forward_y, turn = True):
                            # Get safe cost of destination
                            safe_cost = self.__get_safe_cost(forward_x, forward_y)
                            neighbors.append((forward_x, forward_y, new_orientation, safe_cost + 10))

                        # Corresponding Command: BL00
                        if self.arena.is_reachable(reverse_x, reverse_y, turn = True):
                            if self.arena.is_reachable(x, y+1):
                                # Get safe cost of destination
                                safe_cost = self.__get_safe_cost(reverse_x, reverse_y)
                                neighbors.append((reverse_x, reverse_y, new_orientation, safe_cost + 10))
                            elif strict == False:
                                # Get safe cost of destination + additionally cost for unreachable intermediate (+5)
                                safe_cost = self.__get_safe_cost(reverse_x, reverse_y)
                                neighbors.append((reverse_x, reverse_y, new_orientation, safe_cost + 20))

                    # Facing NORTH -> Facing WEST
                    if new_orientation == Direction.WEST:
                        forward_x = x - bigger_change
                        forward_y = y + smaller_change
                        reverse_x = x + bigger_change
                        reverse_y = y - smaller_change

                        # Corresponding Command: FL00
                        if self.arena.is_reachable(forward_x - 1, forward_y, turn = True):
                            safe_cost = self.__get_safe_cost(forward_x, forward_y)
                            neighbors.append((forward_x, forward_y, new_orientation, safe_cost + 10))

                        # Corresponding Command: BR00
                        if self.arena.is_reachable(reverse_x, reverse_y, turn = True):
                            if self.arena.is_reachable(x, y + 1):
                                safe_cost = self.__get_safe_cost(reverse_x, reverse_y)
                                neighbors.append((reverse_x, reverse_y, new_orientation, safe_cost + 10))
                            elif strict == False:
                                safe_cost = self.__get_safe_cost(reverse_x, reverse_y)
                                neighbors.append((reverse_x, reverse_y, new_orientation, safe_cost + 20))


                elif orientation == Direction.EAST:
                    # Facing EAST -> Facing NORTH
                    if new_orientation == Direction.NORTH :
                        forward_x = x + smaller_change
                        forward_y = y + bigger_change
                        reverse_x = x - smaller_change
                        reverse_y = y - bigger_change

                        # Corresponding Command: FL00
                        if self.arena.is_reachable(forward_x, forward_y + 1, turn = True):
                            safe_cost = self.__get_safe_cost(forward_x, forward_y)
                            neighbors.append((forward_x, forward_y, new_orientation, safe_cost + 10))

                        # Corresponding Command: BR00
                        if self.arena.is_reachable(reverse_x, reverse_y, turn = True):
                            if self.arena.is_reachable(x+1, y):
                                safe_cost = self.__get_safe_cost(reverse_x, reverse_y)
                                neighbors.append((reverse_x, reverse_y, new_orientation, safe_cost + 10))
                            elif strict == False:
                                safe_cost = self.__get_safe_cost(reverse_x, reverse_y)
                                neighbors.append((reverse_x, reverse_y, new_orientation, safe_cost + 20))


                    # Facing EAST -> Facing SOUTH
                    if new_orientation == Direction.SOUTH:
                        forward_x = x + smaller_change
                        forward_y = y - bigger_change
                        reverse_x = x - smaller_change
                        reverse_y = y + bigger_change

                        # Corresponding Command: FR00
                        if self.arena.is_reachable(forward_x, forward_y - 1, turn = True):
                            safe_cost = self.__get_safe_cost(forward_x, forward_y)
                            neighbors.append((forward_x, forward_y, new_orientation, safe_cost + 10))

                        # Corresponding Command: BL00
                        if self.arena.is_reachable(reverse_x, reverse_y, turn = True):
                            if self.arena.is_reachable(x + 1, y):
                                safe_cost = self.__get_safe_cost(reverse_x, reverse_y)
                                neighbors.append((reverse_x, reverse_y, new_orientation, safe_cost + 10))
                            elif strict == False:
                                safe_cost = self.__get_safe_cost(reverse_x, reverse_y)
                                neighbors.append((reverse_x, reverse_y, new_orientation, safe_cost + 20))


                elif orientation == Direction.SOUTH:
                    # Facing SOUTH -> Facing EAST
                    if new_orientation == Direction.EAST:
                        forward_x = x + bigger_change
                        forward_y = y - smaller_change
                        reverse_x = x - bigger_change
                        reverse_y = y + smaller_change

                        # Corresponding Command: FL00
                        if self.arena.is_reachable(forward_x + 1, forward_y, turn = True):
                            safe_cost = self.__get_safe_cost(forward_x, forward_y)
                            neighbors.append((forward_x, forward_y, new_orientation, safe_cost + 10))

                        # Corresponding Command: BR00
                        if self.arena.is_reachable(reverse_x, reverse_y, turn = True):
                            if self.arena.is_reachable( x , y - 1):
                                safe_cost = self.__get_safe_cost(reverse_x, reverse_y)
                                neighbors.append((reverse_x, reverse_y, new_orientation, safe_cost + 10))
                            elif strict == False:
                                safe_cost = self.__get_safe_cost(reverse_x, reverse_y)
                                neighbors.append((reverse_x, reverse_y, new_orientation, safe_cost + 20))


                    # Facing SOUTH -> Facing WEST
                    if new_orientation == Direction.WEST:
                        forward_x = x - bigger_change
                        forward_y = y - smaller_change
                        reverse_x = x + bigger_change
                        reverse_y = y + smaller_change

                        # Corresponding Command: FR00
                        if self.arena.is_reachable(forward_x-1, forward_y, turn = True):
                            safe_cost = self.__get_safe_cost(forward_x, forward_y)
                            neighbors.append((forward_x, forward_y, new_orientation, safe_cost + 10))

                        # Corresponding Command: BL00
                        if self.arena.is_reachable(reverse_x, reverse_y, turn = True):
                            if self.arena.is_reachable(x, y-1):
                                safe_cost = self.__get_safe_cost(reverse_x, reverse_y)
                                neighbors.append((reverse_x, reverse_y, new_orientation, safe_cost + 10))
                            elif strict == False:
                                safe_cost = self.__get_safe_cost(reverse_x, reverse_y)
                                neighbors.append((reverse_x, reverse_y, new_orientation, safe_cost + 20))

                elif orientation == Direction.WEST:
                    # Facing WEST -> Facing SOUTH
                    if new_orientation == Direction.SOUTH:
                        forward_x = x - smaller_change
                        forward_y = y - bigger_change
                        reverse_x = x + smaller_change
                        reverse_y = y + bigger_change

                        # Corresponding Command: FL00
                        if self.arena.is_reachable(forward_x, forward_y-1, turn = True):
                            safe_cost = self.__get_safe_cost(forward_x, forward_y)
                            neighbors.append((forward_x, forward_y, new_orientation, safe_cost + 10))

                        # Corresponding Command: BR00
                        if self.arena.is_reachable(reverse_x, reverse_y, turn = True):
                            if self.arena.is_reachable(x-1, y):
                                safe_cost = self.__get_safe_cost(reverse_x, reverse_y)
                                neighbors.append((reverse_x, reverse_y, new_orientation, safe_cost + 10))
                            elif strict == False:
                                safe_cost = self.__get_safe_cost(reverse_x, reverse_y)
                                neighbors.append((reverse_x, reverse_y, new_orientation, safe_cost + 20))

                        # Facing WEST -> Facing NORTH
                        if new_orientation == Direction.NORTH:
                            forward_x = x - smaller_change
                            forward_y = y + bigger_change
                            reverse_x = x + smaller_change
                            reverse_y = y - bigger_change

                            # Corresponding Command: FR00
                            if self.arena.is_reachable(forward_x, forward_y+1, turn = True):
                                safe_cost = self.__get_safe_cost(forward_x, forward_y)
                                neighbors.append((forward_x, forward_y, new_orientation, safe_cost + 10))

                            # Corresponding Command: BL00
                            if self.arena.is_reachable(reverse_x, reverse_y, turn = True):
                                if self.arena.is_reachable(x-1, y):
                                    safe_cost = self.__get_safe_cost(reverse_x, reverse_y)
                                    neighbors.append((reverse_x, reverse_y, new_orientation, safe_cost + 10))
                                elif strict == False:
                                    safe_cost = self.__get_safe_cost(reverse_x, reverse_y)
                                    neighbors.append((reverse_x, reverse_y, new_orientation, safe_cost + 20))
        return neighbors

    def __path_cost_generator(self, states: List[GridCell]):
        """Generate the path cost between the input states and update the tables accordingly

        Args:
            states (List[GridCell]): cell states to visit
        """
        def __record_path(start, end, parent: dict, cost: int):

            # Update cost table for the (start,end) and (end,start) edges
            self.cost_table[(start, end)] = cost
            self.cost_table[(end, start)] = cost

            path = []
            cursor = (end.x, end.y, end.direction)

            while cursor in parent:
                path.append(cursor)
                cursor = parent[cursor]

            path.append(cursor)

            # Update path table for the (start,end) and (end,start) edges, with the (start,end) edge being the reversed path
            self.path_table[(start, end)] = path[::-1]
            self.path_table[(end, start)] = path

        def __astar_search(start: GridCell, end: GridCell):

            dist_between = self.__compute_distance_between(start, end)

            # If it is already done before, return
            if (start, end) in self.path_table:
                return

            # Heuristic to guide the search: 'distance' is calculated by f = g + h
            # g is the actual distance moved so far from the start node to current node
            # h is the heuristic distance from current node to end node
            g_distance = {(start.x, start.y, start.direction): 0}

            # format of each item in heap: (f_distance of node, x coord of node, y coord of node)
            # heap in Python is a min-heap
            heap = [(dist_between, start.x, start.y, start.direction)]
            parent = dict()
            visited = set()

            while heap:
                # Pop the node with the smallest distance
                _, cur_x, cur_y, cur_direction = heapq.heappop(heap)
                
                # Skip if the node has already been explored
                if (cur_x, cur_y, cur_direction) in visited:
                    continue

                # Goal testing, checking if popped node is the goal node
                if end.is_equal(cur_x, cur_y, cur_direction):
                    __record_path(start, end, parent, g_distance[(cur_x, cur_y, cur_direction)])
                    return

                visited.add((cur_x, cur_y, cur_direction))
                cur_distance = g_distance[(cur_x, cur_y, cur_direction)]

                for next_x, next_y, new_direction, safe_cost in self.__get_neighbors(cur_x, cur_y, cur_direction):
                    if (next_x, next_y, new_direction) in visited:
                        continue

                    move_cost = self.__calc_rotation_cost(new_direction, cur_direction) * TURN_FACTOR + 1 + safe_cost

                    # the cost to check if any obstacles that considered too near the robot; if it
                    # safe_cost =

                    # new cost is calculated by the cost to reach current state + cost to move from
                    # current state to new state + heuristic cost from new state to end state
                    next_cost = \
                        cur_distance + \
                        move_cost + \
                        self.__compute_distance_between(x1 = next_x, y1 = next_y, x2 = end.x, y2 = end.y)

                    if (next_x, next_y, new_direction) not in g_distance or \
                            g_distance[(next_x, next_y, new_direction)] > cur_distance + move_cost:
                        g_distance[(next_x, next_y, new_direction)] = cur_distance + move_cost
                        parent[(next_x, next_y, new_direction)] = (cur_x, cur_y, cur_direction)

                        heapq.heappush(heap, (next_cost, next_x, next_y, new_direction))
                
        # Nested loop through all the state pairings
        for i in range(len(states) - 1):
            for j in range(i + 1, len(states)):
                __astar_search(states[i], states[j])