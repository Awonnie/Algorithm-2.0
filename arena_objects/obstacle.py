from typing import List

from direction import Direction
from .grid_cell import GridCell
from .helper import is_valid
from consts import EXPANDED_CELL, SCREENSHOT_COST

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

    def get_view_state(self, retrying) -> List[GridCell]:
        """Constructs the list of CellStates from which the robot can view the symbol on the obstacle

        Returns:
            List[GridCell]: Valid cell states where robot can be positioned to view the symbol on the obstacle
        """
        cells = []
        # If the obstacle is facing north, then robot's cell state must be facing south
       
        if self.direction == Direction.NORTH:
            if retrying == False:
                # Or (x, y + 3)
                if is_valid(self.x, self.y + 1 + EXPANDED_CELL * 2):
                    cells.append(GridCell(
                        self.x, self.y + 1 + EXPANDED_CELL * 2, Direction.SOUTH, self.obstacle_id, 5))
                # Or (x, y + 4)
                if is_valid(self.x, self.y + 2 + EXPANDED_CELL * 2):
                    cells.append(GridCell(
                        self.x, self.y + 2 + EXPANDED_CELL * 2, Direction.SOUTH, self.obstacle_id, 0))

                # Or (x + 1, y + 3)
                # if is_valid(self.x + 1, self.y + 1 + EXPANDED_CELL * 2):
                #     cells.append(GridCell(self.x + 1, self.y + 1 + EXPANDED_CELL * 2, Direction.SOUTH, self.obstacle_id, SCREENSHOT_COST*10))
                # # Or (x - 1, y + 3)
                # if is_valid(self.x - 1, self.y + 1 + EXPANDED_CELL * 2):
                #     cells.append(GridCell(self.x - 1, self.y + 1 + EXPANDED_CELL * 2, Direction.SOUTH, self.obstacle_id, SCREENSHOT_COST*10))

                # Or (x + 1, y + 4)
                if is_valid(self.x + 1, self.y + 2 + EXPANDED_CELL * 2):
                    cells.append(GridCell(self.x + 1, self.y + 2 + EXPANDED_CELL *
                                 2, Direction.SOUTH, self.obstacle_id, SCREENSHOT_COST))
                # Or (x - 1, y + 4)
                if is_valid(self.x - 1, self.y + 2 + EXPANDED_CELL * 2):
                    cells.append(GridCell(self.x - 1, self.y + 2 + EXPANDED_CELL *
                                 2, Direction.SOUTH, self.obstacle_id, SCREENSHOT_COST))

            elif retrying == True:
                # Or (x, y + 4)
                if is_valid(self.x, self.y + 2 + EXPANDED_CELL * 2):
                    cells.append(GridCell(
                        self.x, self.y + 2 + EXPANDED_CELL * 2, Direction.SOUTH, self.obstacle_id, 0))
                # Or (x, y + 5)
                if is_valid(self.x, self.y + 3 + EXPANDED_CELL * 2):
                    cells.append(GridCell(
                        self.x, self.y + 3 + EXPANDED_CELL * 2, Direction.SOUTH, self.obstacle_id, 0))
                # Or (x + 1, y + 4)
                if is_valid(self.x + 1, self.y + 2 + EXPANDED_CELL * 2):
                    cells.append(GridCell(self.x + 1, self.y + 2 + EXPANDED_CELL *
                                 2, Direction.SOUTH, self.obstacle_id, SCREENSHOT_COST))
                # Or (x - 1, y + 4)
                if is_valid(self.x - 1, self.y + 2 + EXPANDED_CELL * 2):
                    cells.append(GridCell(self.x - 1, self.y + 2 + EXPANDED_CELL *
                                 2, Direction.SOUTH, self.obstacle_id, SCREENSHOT_COST))

        # If obstacle is facing south, then robot's cell state must be facing north
        elif self.direction == Direction.SOUTH:

            if retrying == False:
                # Or (x, y - 3)
                if is_valid(self.x, self.y - 1 - EXPANDED_CELL * 2):
                    cells.append(GridCell(
                        self.x, self.y - 1 - EXPANDED_CELL * 2, Direction.NORTH, self.obstacle_id, 5))
                # Or (x, y - 4)
                if is_valid(self.x, self.y - 2 - EXPANDED_CELL * 2):
                    cells.append(GridCell(
                        self.x, self.y - 2 - EXPANDED_CELL * 2, Direction.NORTH, self.obstacle_id, 0))

                # Or (x + 1, y - 3)
                # if is_valid(self.x + 1, self.y - 1 - EXPANDED_CELL * 2):
                #     cells.append(GridCell(self.x + 1, self.y - 1 - EXPANDED_CELL * 2, Direction.NORTH, self.obstacle_id, SCREENSHOT_COST*10))
                # # Or (x - 1, y - 3)
                # if is_valid(self.x - 1, self.y - 1 - EXPANDED_CELL * 2):
                #     cells.append(GridCell(self.x - 1, self.y - 1 - EXPANDED_CELL * 2, Direction.NORTH, self.obstacle_id, SCREENSHOT_COST*10))

                # Or (x + 1, y - 4)
                if is_valid(self.x + 1, self.y - 2 - EXPANDED_CELL * 2):
                    cells.append(GridCell(self.x + 1, self.y - 2 - EXPANDED_CELL *
                                 2, Direction.NORTH, self.obstacle_id, SCREENSHOT_COST))
                # Or (x - 1, y - 4)
                if is_valid(self.x - 1, self.y - 2 - EXPANDED_CELL * 2):
                    cells.append(GridCell(self.x - 1, self.y - 2 - EXPANDED_CELL *
                                 2, Direction.NORTH, self.obstacle_id, SCREENSHOT_COST))

            elif retrying == True:
                # Or (x, y - 4)
                if is_valid(self.x, self.y - 2 - EXPANDED_CELL * 2):
                    cells.append(GridCell(
                        self.x, self.y - 2 - EXPANDED_CELL * 2, Direction.NORTH, self.obstacle_id, 0))
                # Or (x, y - 5)
                if is_valid(self.x, self.y - 3 - EXPANDED_CELL * 2):
                    cells.append(GridCell(
                        self.x, self.y - 3 - EXPANDED_CELL * 2, Direction.NORTH, self.obstacle_id, 0))
                # Or (x + 1, y - 4)
                if is_valid(self.x + 1, self.y - 2 - EXPANDED_CELL * 2):
                    cells.append(GridCell(self.x + 1, self.y - 2 - EXPANDED_CELL *
                                 2, Direction.NORTH, self.obstacle_id, SCREENSHOT_COST))
                # Or (x - 1, y - 4)
                if is_valid(self.x - 1, self.y - 2 - EXPANDED_CELL * 2):
                    cells.append(GridCell(self.x - 1, self.y - 2 - EXPANDED_CELL *
                                 2, Direction.NORTH, self.obstacle_id, SCREENSHOT_COST))

        # If obstacle is facing east, then robot's cell state must be facing west
        elif self.direction == Direction.EAST:

            if retrying == False:
                # Or (x + 3,y)
                if is_valid(self.x + 1 + EXPANDED_CELL * 2, self.y):
                    cells.append(GridCell(self.x + 1 + EXPANDED_CELL * 2,
                                 self.y, Direction.WEST, self.obstacle_id, 5))
                # Or (x + 4,y)
                if is_valid(self.x + 2 + EXPANDED_CELL * 2, self.y):
                    # print(f"Obstacle facing east, Adding {self.x + 2 + EXPANDED_CELL * 2}, {self.y}")
                    cells.append(GridCell(self.x + 2 + EXPANDED_CELL * 2,
                                 self.y, Direction.WEST, self.obstacle_id, 0))

                # Or (x + 3,y + 1)
                # if is_valid(self.x + 1 + EXPANDED_CELL * 2, self.y + 1):
                #     #print(f"Obstacle facing east, Adding {self.x + 2 + EXPANDED_CELL * 2}, {self.y + 1}")
                #     cells.append(GridCell(self.x + 1 + EXPANDED_CELL * 2, self.y + 1, Direction.WEST, self.obstacle_id, SCREENSHOT_COST*10))
                # # Or (x + 3,y - 1)
                # if is_valid(self.x + 1 + EXPANDED_CELL * 2, self.y - 1):
                #     #print(f"Obstacle facing east, Adding {self.x + 2 + EXPANDED_CELL * 2}, {self.y - 1}")
                #     cells.append(GridCell(self.x + 1 + EXPANDED_CELL * 2, self.y - 1, Direction.WEST, self.obstacle_id, SCREENSHOT_COST*10))

                # Or (x + 4, y + 1)
                if is_valid(self.x + 2 + EXPANDED_CELL * 2, self.y + 1):
                    cells.append(GridCell(self.x + 2 + EXPANDED_CELL * 2, self.y +
                                 1, Direction.WEST, self.obstacle_id, SCREENSHOT_COST))
                # Or (x + 4, y - 1)
                if is_valid(self.x + 2 + EXPANDED_CELL * 2, self.y - 1):
                    cells.append(GridCell(self.x + 2 + EXPANDED_CELL * 2, self.y -
                                 1, Direction.WEST, self.obstacle_id, SCREENSHOT_COST))

            elif retrying == True:
                # Or (x + 4, y)
                if is_valid(self.x + 2 + EXPANDED_CELL * 2, self.y):
                    cells.append(GridCell(self.x + 2 + EXPANDED_CELL * 2,
                                 self.y, Direction.WEST, self.obstacle_id, 0))
                # Or (x + 5, y)
                if is_valid(self.x + 3 + EXPANDED_CELL * 2, self.y):
                    cells.append(GridCell(self.x + 3 + EXPANDED_CELL * 2,
                                 self.y, Direction.WEST, self.obstacle_id, 0))
                # Or (x + 4,y + 1)
                if is_valid(self.x + 2 + EXPANDED_CELL * 2, self.y + 1):
                    cells.append(GridCell(self.x + 2 + EXPANDED_CELL * 2, self.y +
                                 1, Direction.WEST, self.obstacle_id, SCREENSHOT_COST))
                # Or (x + 4,y - 1)
                if is_valid(self.x + 2 + EXPANDED_CELL * 2, self.y - 1):
                    cells.append(GridCell(self.x + 2 + EXPANDED_CELL * 2, self.y -
                                 1, Direction.WEST, self.obstacle_id, SCREENSHOT_COST))

        # If obstacle is facing west, then robot's cell state must be facing east
        elif self.direction == Direction.WEST:
            # It can be (x - 2,y)
            # if is_valid(self.x - EXPANDED_CELL * 2, self.y):
            #     cells.append(GridCell(self.x - EXPANDED_CELL * 2, self.y, Direction.EAST, self.obstacle_id, 0))

            if retrying == False:
                # Or (x - 3, y)
                if is_valid(self.x - 1 - EXPANDED_CELL * 2, self.y):
                    cells.append(GridCell(self.x - 1 - EXPANDED_CELL * 2,
                                 self.y, Direction.EAST, self.obstacle_id, 5))
                # Or (x - 4, y)
                if is_valid(self.x - 2 - EXPANDED_CELL * 2, self.y):
                    cells.append(GridCell(self.x - 2 - EXPANDED_CELL * 2,
                                 self.y, Direction.EAST, self.obstacle_id, 0))

                # Or (x - 3,y + 1)
                # if is_valid(self.x - 1 - EXPANDED_CELL * 2, self.y + 1):
                #     cells.append(GridCell(self.x - 1 - EXPANDED_CELL * 2, self.y + 1, Direction.EAST, self.obstacle_id, SCREENSHOT_COST*10))
                # # Or (x - 3,y - 1)
                # if is_valid(self.x - 1 - EXPANDED_CELL * 2, self.y - 1):
                #     cells.append(GridCell(self.x - 1 - EXPANDED_CELL * 2, self.y - 1, Direction.EAST, self.obstacle_id, SCREENSHOT_COST*10))

                # Or (x - 4, y + 1)
                if is_valid(self.x - 2 - EXPANDED_CELL * 2, self.y + 1):
                    cells.append(GridCell(self.x - 2 - EXPANDED_CELL * 2, self.y +
                                 1, Direction.EAST, self.obstacle_id, SCREENSHOT_COST))
                # Or (x - 4, y - 1)
                if is_valid(self.x - 2 - EXPANDED_CELL * 2, self.y - 1):
                    cells.append(GridCell(self.x - 2 - EXPANDED_CELL * 2, self.y -
                                 1, Direction.EAST, self.obstacle_id, SCREENSHOT_COST))

            elif retrying == True:
                # Or (x - 4, y)
                if is_valid(self.x - 2 - EXPANDED_CELL * 2, self.y):
                    cells.append(GridCell(self.x - 2 - EXPANDED_CELL * 2,
                                 self.y, Direction.EAST, self.obstacle_id, 0))
                # Or (x - 5, y)
                if is_valid(self.x - 3 - EXPANDED_CELL * 2, self.y):
                    cells.append(GridCell(self.x - 3 - EXPANDED_CELL * 2,
                                 self.y, Direction.EAST, self.obstacle_id, 0))
                # Or (x - 4, y + 1)
                if is_valid(self.x - 2 - EXPANDED_CELL * 2, self.y + 1):
                    cells.append(GridCell(self.x - 2 - EXPANDED_CELL * 2, self.y +
                                 1, Direction.EAST, self.obstacle_id, SCREENSHOT_COST))
                # Or (x - 4, y - 1)
                if is_valid(self.x - 2 - EXPANDED_CELL * 2, self.y - 1):
                    cells.append(GridCell(self.x - 2 - EXPANDED_CELL * 2, self.y -
                                 1, Direction.EAST, self.obstacle_id, SCREENSHOT_COST))

        # print(f"Cells: {cells}")
        return cells