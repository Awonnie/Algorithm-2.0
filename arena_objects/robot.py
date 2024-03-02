from typing import List

from direction import Direction
from .grid_cell import GridCell

class Robot:
    def __init__(self, center_x: int, center_y: int, start_direction: Direction):
        """Robot object class

        Args:
            center_x (int): x coordinate of center of robot
            center_y (int): y coordinate of center of robot
            start_direction (Direction): Direction robot is facing at the start

        Internals:
            states: List of cell states of the robot's historical path
        """
        self.robot_cell: List[GridCell] = [GridCell(center_x, center_y, start_direction)]

    def get_robot_cell(self):
        """Returns the starting cell state of the robot

        Returns:
            GridCell: starting cell state of robot (x,y,d)
        """
        return self.robot_cell[0]