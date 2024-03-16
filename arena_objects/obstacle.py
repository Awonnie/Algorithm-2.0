from typing import List

from consts import SCREENSHOT_COST, VIRTUAL_CELLS
from direction import Direction

from .grid_cell import GridCell
from .helper import is_valid_position


class Obstacle(GridCell):
    """Obstacle class, inherited from GridCell"""

    def __init__(self, x: int, y: int, direction: Direction, obstacle_id: int):
        super().__init__(x, y, direction)
        self.obstacle_id = obstacle_id

    def __eq__(self, other):
        """Checks if this obstacle is the same as input in terms of x, y, and direction

        Args:
            other (Obstacle): input obstacle to compare to

        Returns:
            bool: True if same, False otherwise
        """
        return self.x == other.x and self.y == other.y and self.direction == other.direction

    def get_view_gridcells(self, retrying) -> List[GridCell]:
        """Constructs the list of GridCell from which the robot can view the symbol on the obstacle

        Returns:
            List[GridCell]: Valid cell states where robot can be positioned to view the symbol on the obstacle
        """
        cells = []
        extra_cells = VIRTUAL_CELLS + 2 if retrying else VIRTUAL_CELLS + 1
        left_viewing_coord = (0,0)
        right_viewing_coord = (0,0)
        center_viewing_coord = (0,0)
        close_center_viewing_coord = (0,0)
        robot_direction = Direction.NONE


        # If the image is facing NORTH, robot has to be facing SOUTH
        if self.direction == Direction.NORTH:
            center_viewing_coord = (self.x, self.y + extra_cells)
            close_center_viewing_coord = (self.x, self.y + extra_cells - 1)
            left_viewing_coord = (self.x + 1, self.y + extra_cells)
            right_viewing_coord = (self.x - 1, self.y + extra_cells)
            robot_direction = Direction.SOUTH

        # If the image is facing SOUTH, robot has to be facing NORTH
        elif self.direction == Direction.SOUTH:
            center_viewing_coord = (self.x, self.y - extra_cells)
            close_center_viewing_coord = (self.x, self.y - extra_cells + 1)
            left_viewing_coord = (self.x - 1, self.y - extra_cells)
            right_viewing_coord = (self.x + 1, self.y - extra_cells)
            robot_direction = Direction.NORTH

        # If the image is facing WEST, robot has to be facing EAST
        elif self.direction == Direction.WEST:
            center_viewing_coord = (self.x - extra_cells, self.y)
            close_center_viewing_coord = (self.x - extra_cells + 1, self.y)
            left_viewing_coord = (self.x - extra_cells, self.y + 1)
            right_viewing_coord = (self.x - extra_cells, self.y - 1)
            robot_direction = Direction.EAST

        # If the image is facing EAST, robot has to be facing WEST
        elif self.direction == Direction.EAST:
            center_viewing_coord = (self.x + extra_cells, self.y)
            close_center_viewing_coord = (self.x + extra_cells - 1, self.y)
            left_viewing_coord = (self.x + extra_cells, self.y - 1)
            right_viewing_coord = (self.x + extra_cells, self.y + 1)
            robot_direction = Direction.WEST
            
        # Center Positions
        if is_valid_position(center_viewing_coord[0], center_viewing_coord[1]):
            cells.append(GridCell(center_viewing_coord[0], center_viewing_coord[1], robot_direction, self.obstacle_id, 0))
        if is_valid_position(close_center_viewing_coord[0], close_center_viewing_coord[1]):
            cells.append(GridCell(close_center_viewing_coord[0], close_center_viewing_coord[1], robot_direction, self.obstacle_id, 0))
                
        # Left Position
        if is_valid_position(left_viewing_coord[0], left_viewing_coord[1]):
            cells.append(GridCell(left_viewing_coord[0], left_viewing_coord[1], robot_direction, self.obstacle_id, SCREENSHOT_COST))

        # Right Position
        if is_valid_position(right_viewing_coord[0], right_viewing_coord[1]):
            cells.append(GridCell(right_viewing_coord[0], right_viewing_coord[1], robot_direction, self.obstacle_id, SCREENSHOT_COST))
                
        return cells