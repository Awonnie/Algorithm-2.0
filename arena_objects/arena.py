from typing import List

from consts import VIRTUAL_CELLS
from .obstacle import Obstacle
from .grid_cell import GridCell
from .robot import Robot

class Arena:
    """
    Arena object that contains the size of the arena and a list of obstacles
    """
    def __init__(
            self, 
            arena_width: int, 
            arena_height: int,
            robot: Robot
            ):
        """
        Args:
            arena_width (int): Size of the arena in the x direction
            arena_height (int): Size of the arena in the y direction
        """
        self.arena_width = arena_width
        self.arena_height = arena_height
        self.robot = robot
        self.obstacles: List[Obstacle] = []

    def add_obstacle(self, obstacle_to_add: Obstacle):
        """Add a new obstacle to the Arena object, ignores if duplicate obstacle

        Args:
            obstacle (Obstacle): Obstacle to be added
        """
        # Loop through the existing obstacles to check for duplicates
        for ob in self.obstacles:
            if ob == obstacle_to_add:
                return

        self.obstacles.append(obstacle_to_add)
        
    def get_obstacles(self):
        """
        Returns the list of obstacles in the arena
        """
        return self.obstacles
    
    def get_robot(self):
        '''
        Returns the robot object
        '''
        return self.robot
    
    def set_robot(self, new_robot):
        '''
        Sets the robot object
        '''
        self.robot = new_robot

    def set_obstacles(self, new_obstacles):
        """
        Sets the obstacles in the arena
        """
        self.obstacles = new_obstacles


    def is_reachable(self, x: int, y: int, turn=False, preTurn=False) -> bool:
        """Checks whether the given x,y coordinate is reachable/safe. Criterion is as such:
        - Must be at least 4 units away in total (x+y) from the obstacle
        - Greater distance (x or y distance) must be at least 3 units away from obstacle

        Args:
            x (int): x-coordinate
            y (int): y-coordinate

        Returns:
            bool: returns true or false
        """
        
        if not self.is_valid_coord(x, y):
            return False

        for ob in self.obstacles:
            if ob.x <= 4 and ob.y <= 4 and x < 4 and y < 4:
                continue

            # Must be at least 4 units away in total (x+y)
            if abs(ob.x - x) + abs(ob.y - y) >= 4:
                continue

            # If max(x,y) is less than 3 units away, consider not reachable
            if turn:
                if max(abs(ob.x - x), abs(ob.y - y)) < VIRTUAL_CELLS:
                    return False
            if preTurn:
                if max(abs(ob.x - x), abs(ob.y - y)) < VIRTUAL_CELLS:
                    return False
            else:
                if max(abs(ob.x - x), abs(ob.y - y)) < 2:
                    return False

        return True

    def is_valid_coord(self, x: int, y: int) -> bool:
        """Checks if given position is within bounds

        Args:
            x (int): x-coordinate
            y (int): y-coordinate

        Returns:
            bool: True if valid, False otherwise
        """
        if x < 1 or x >= self.arena_width - 1 or y < 1 or y >= self.arena_height - 1:
            return False

        return True

    def get_viewing_positions(self, retrying) -> List[List[GridCell]]:
        """
        This function return a list of desired states for the robot to achieve based on the obstacle position and direction.
        The state is the position that the robot can see the image of the obstacle and is safe to reach without collision
        :return: [[GridCell]]
        """
        viewing_positions = []
        for obstacle in self.obstacles:
            if obstacle.direction == 8:
                continue
            else:
                views = [view_gridcell for view_gridcell in obstacle.get_view_gridcells(retrying) if self.is_reachable(view_gridcell.x, view_gridcell.y)]
            viewing_positions.append(views)

        return viewing_positions